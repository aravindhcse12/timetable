"""SQLite replacement for the original MySQL-based ``insert.py``.

The project was originally written against MySQL via ``mysql.connector`` and
``mysql://`` SQLAlchemy URLs.  This module preserves the public surface that
the rest of the project imports from it (``mydb``, ``mycursor``,
``show_all_tables``, ``updateF``, ``deleteF``, ``create_table``) but is now
backed by ``sqlite3`` and a SQLAlchemy SQLite engine pointing at the same
database file used by Flask-SQLAlchemy.

To keep the rest of the codebase (``appy.py``, ``fac.py``) untouched, the
cursor wrapper transparently rewrites MySQL-only SQL such as
``SHOW TABLES``, ``SHOW TABLES WHERE Tables_in_<db> LIKE ...`` and
``SHOW COLUMNS FROM <table>`` into SQLite equivalents.
"""

import os
import re
import sqlite3

from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Database location -- a single SQLite file alongside this script.
# ``appy.py`` configures Flask-SQLAlchemy to use the same path so that the
# ORM models and the raw ``sqlite3`` connection share the same database.
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "jntuk1.db")

# ---------------------------------------------------------------------------
# SQLAlchemy engine (used by ``create_table`` for the fast paths).
# ---------------------------------------------------------------------------
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)
meta = MetaData()

Session = sessionmaker(bind=engine)
session = Session()


# ---------------------------------------------------------------------------
# MySQL -> SQLite SQL translation helpers.
# ---------------------------------------------------------------------------

# `SHOW COLUMNS FROM `tbl``  ->  SELECT name FROM pragma_table_info('tbl')
_SHOW_COLUMNS_RE = re.compile(
    r"^\s*SHOW\s+COLUMNS\s+FROM\s+[`\"]?(?P<tbl>[^`\"\s;]+)[`\"]?\s*;?\s*$",
    re.IGNORECASE,
)

# `SHOW TABLES WHERE Tables_in_<db> LIKE '<pat>';`
_SHOW_TABLES_LIKE_RE = re.compile(
    r"^\s*SHOW\s+TABLES\s+WHERE\s+Tables_in_\w+\s+LIKE\s+'(?P<pat>[^']*)'\s*;?\s*$",
    re.IGNORECASE,
)

# `SHOW TABLES;`
_SHOW_TABLES_RE = re.compile(r"^\s*SHOW\s+TABLES\s*;?\s*$", re.IGNORECASE)


def _translate_sql(sql):
    """Translate a small subset of MySQL-specific SQL to SQLite."""

    m = _SHOW_COLUMNS_RE.match(sql)
    if m:
        tbl = m.group("tbl").replace("'", "''")
        # pragma_table_info(name) returns rows of (cid, name, type, notnull,
        # dflt_value, pk).  Selecting just ``name`` keeps callers that read
        # ``row[0]`` (field name) working unchanged.
        return f"SELECT name FROM pragma_table_info('{tbl}')"

    m = _SHOW_TABLES_LIKE_RE.match(sql)
    if m:
        pat = m.group("pat").replace("'", "''")
        return (
            "SELECT name FROM sqlite_master WHERE type='table' "
            f"AND name LIKE '{pat}'"
        )

    if _SHOW_TABLES_RE.match(sql):
        return "SELECT name FROM sqlite_master WHERE type='table'"

    return sql


# ---------------------------------------------------------------------------
# Lightweight wrappers so calling code can keep using ``mydb`` / ``mycursor``
# with the same API it had with ``mysql.connector``
# (``cursor(buffered=True)``, ``mydb.commit()``, ...).
# ---------------------------------------------------------------------------


class _SQLiteCursorWrapper:
    """Thin wrapper around ``sqlite3.Cursor`` with MySQL-compatibility shims."""

    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    # Delegate any other attribute access to the underlying cursor.
    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def execute(self, sql, params=None):
        sql = _translate_sql(sql)
        if params is None:
            return self._cursor.execute(sql)
        return self._cursor.execute(sql, params)

    def executemany(self, sql, seq_of_params):
        sql = _translate_sql(sql)
        return self._cursor.executemany(sql, seq_of_params)

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchone(self):
        return self._cursor.fetchone()

    def close(self):
        self._cursor.close()


class _SQLiteConnection:
    """Connection wrapper that mimics ``mysql.connector`` semantics."""

    def __init__(self, path):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        # Be tolerant of concurrent writes from SQLAlchemy.
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA busy_timeout=5000;")

    def cursor(self, *args, **kwargs):  # ignore buffered=True etc.
        return _SQLiteCursorWrapper(self._conn)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


mydb = _SQLiteConnection(DB_PATH)
mycursor = mydb.cursor()


# ---------------------------------------------------------------------------
# Public helpers used throughout appy.py / fac.py
# ---------------------------------------------------------------------------


def show_all_tables(table_name):
    """Return True if a table with ``table_name`` already exists (case-insensitive)."""

    cur = mydb.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0].lower() for row in cur.fetchall()]
    return table_name.lower() in tables


def updateF(oldname, newname):
    """Rename a faculty timetable table."""

    cur = mydb.cursor()
    if show_all_tables(oldname):
        cur.execute('ALTER TABLE "{0}" RENAME TO "{1}"'.format(oldname, newname))
        mydb.commit()


def deleteF(table_name):
    """Drop a faculty timetable table."""

    cur = mydb.cursor()
    if show_all_tables(table_name):
        cur.execute('DROP TABLE "{0}"'.format(table_name))
        mydb.commit()


def _create_via_sqlalchemy(name, periods):
    """Create a timetable table using the SQLAlchemy Table API.

    Used for the two original fast-paths (8 periods/6 days and
    7 periods/6 days).  Kept for behavioural parity with the old code.
    """

    already_exists = show_all_tables(name)

    columns = [Column("Day", String(50))]
    for i in range(1, periods + 1):
        columns.append(Column(str(i), String(250)))

    table = Table(name, meta, *columns, extend_existing=True)
    meta.create_all(engine)

    if already_exists:
        return

    day_list = ["MON", "TUE", "WED", "THU", "FRI", "SAT"]
    placeholders = ["--"] * periods

    with engine.begin() as conn:
        for day in day_list:
            conn.execute(table.insert().values([day, *placeholders]))


def create_table(name, periods, day):
    """Create a faculty/lab/class timetable table with the given shape."""

    if periods == 8 and day == 6:
        _create_via_sqlalchemy(name, 8)
        return

    if periods == 7 and day == 6:
        _create_via_sqlalchemy(name, 7)
        return

    day_list = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    cur = mydb.cursor()
    cur.execute('CREATE TABLE "{0}"("DAY" VARCHAR(10))'.format(name))
    mydb.commit()

    for count, j in enumerate(day_list, start=1):
        if count > day:
            break
        cur.execute('INSERT INTO "{0}" VALUES (?)'.format(name), (j,))

    for i in range(1, periods + 1):
        cur.execute(
            'ALTER TABLE "{0}" ADD "{1}" VARCHAR(256) DEFAULT \'--\''.format(name, i)
        )

    mydb.commit()








