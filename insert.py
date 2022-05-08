import pandas as pd
#import openpyxl
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sympy import true

engine = create_engine('mysql://root:''@localhost/jntuk1', echo = True)
meta = MetaData()

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind = engine)
session = Session()


import mysql.connector

mydb = mysql.connector.connect(
host="localhost",
user="root",
password="",
database="jntuk1")

mycursor = mydb.cursor(buffered=True)


def show_all_tables(table_name):

   mycursor = mydb.cursor(buffered=True)

   mycursor.execute("SHOW TABLES")

   tables=mycursor.fetchall()

   l1=[]
   for i in tables:
      l1.append(i[0])

   if(table_name in l1):
      return True
   else:
      return False



"""data = {
  "calories": [420, 380, 390],
  "duration": [50, 40, 45]
}"""

#myvar = pd.DataFrame(data)



#df=pd.DataFrame(l1)

#myvar.to_excel("data1.xlsx")

#df = pd.read_csv('data.csv')
def updateF(oldname,newname):
   #faculty edit
   mycursor = mydb.cursor(buffered=True)
   if(show_all_tables(oldname)):
      mycursor.execute("ALTER TABLE `{0}` RENAME TO `{1}`".format(oldname,newname))

def deleteF(table_name):
   mycursor = mydb.cursor(buffered=True)
   if(show_all_tables(table_name)):

      mycursor.execute("DROP TABLE `{0}` ".format(table_name))




def create_table(name,periods,day):

   mycursor = mydb.cursor(buffered=True)


   if(periods==8 and day==6):

      student=Table(

      name, meta,Column('Day', String(50)), 


      Column('1', String(250)), 
      Column('2', String(250)),
      Column('3', String(250)),
      Column('4', String(250)),
      Column('5', String(250)),
      Column('6', String(250)),
      Column('7', String(250)),
      Column('8', String(250)),extend_existing=True)

      meta.create_all(engine)

      conn = engine.connect()
   
      conn.execute(student.insert().values(('MON','--','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('TUE','--','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('WED','--','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('THU','--','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('FRI','--','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('SAT','--','--','--','--','--','--','--','--')))
      mydb.commit()
      
   elif(periods==7 and day==6):

      student=Table(

      name, meta,Column('Day', String(50)), 
      Column('1', String(250)), 
      Column('2', String(250)),
      Column('3', String(250)),
      Column('4', String(250)),
      Column('5', String(250)),
      Column('6', String(250)),
      Column('7', String(250)),extend_existing=True)

      meta.create_all(engine)

      conn = engine.connect()
   
      conn.execute(student.insert().values(('MON','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('TUE','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('WED','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('THU','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('FRI','--','--','--','--','--','--','--')))
      conn.execute(student.insert().values(('SAT','--','--','--','--','--','--','--')))
      mydb.commit()

   else:

      day_list=['MON','TUE','WED','THU','FRI','SAT','SUN']


      mycursor.execute("CREATE TABLE `{0}`(`DAY` VARCHAR(10))".format(name))

      mydb.commit()

      count=1

      print("days",day,"periods",periods)
      for j in day_list:

         if(count<=day):

            mycursor.execute("INSERT INTO `{0}` VALUES ('{1}')".format(name,j))

            #mydb.commit()
            #INSERT INTO `raina`(`DAY`) VALUES ([value-1])

         else:
            break

         count+=1

      for i in range(1,periods+1):

         mycursor.execute("ALTER TABLE `{0}` ADD `{1}` VARCHAR(256)  DEFAULT '--'".format(name,i))

      mydb.commit()

   






