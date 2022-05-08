from appy import *
@app.route('/')
def dashboard():
    print("dashboad")
    return render_template("dashboard.html")
 
#Creating Teacheradd table for our jntuk database
class Teacheradd(db.Model):

    __tablename__ = "Facultyadd"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    branch = db.Column(db.String(20))
    role=db.Column(db.String(20))
    work_load= db.Column(db.Integer)


    def __init__(self, name,branch,role):
        self.name = name
        self.branch=branch
        self.role=role
        self.work_load=0
        
db.create_all()



#query on all our teacher data
@app.route('/teacheradd')
def teacheradd():
    all_data = Teacheradd.query.all()

    return render_template("teacheradd.html", employees = all_data,count=len(all_data))


#this route is for inserting teacher data to mysql database via html forms
@app.route('/insert', methods = ['POST'])
def insert():
 
    if request.method == 'POST':
 
        name = request.form['name'].lower()#challa
        count=Teacheradd.query.filter_by(name=name).count()
        if(count==0):
            branch=request.form['branch']

            role=request.form['role']
        
            my_data = Teacheradd(name,branch,role)
            db.session.add(my_data)
            db.session.commit()#insert
        else:
            flash("can not add name is already present ")

        flag=show_all_tables(name)

        if(flag is False):
            create_table(name)

            flash("Faculty Inserted Successfully")
        else:
            flash("Faculty is already present ")

        return redirect(url_for('teacheradd'))
 
 
#this is our update route where we are going to update our Faculty
@app.route('/updateteacher/<name1>', methods = ['GET', 'POST'])
def updateteacher(name1):
 
    if request.method == 'POST':
        my_data = Teacheradd.query.get(request.form.get('id'))
 
    
        my_data.name = request.form['name'].lower()
        my_data.branch=request.form['branch']
        my_data.role=request.form['role']
        updateF(name1,request.form['name'])
        db.session.commit()#insert
    
        flash("Employee Updated successfully")
 
        return redirect(url_for('teacheradd'))
 
 
 
#This route is for deleting our faculty
@app.route('/deleteteacher/<id>/', methods = ['GET', 'POST'])
def deleteteacher(id):
    my_data = Teacheradd.query.get(id)

    db.session.delete(my_data)

    db.session.commit()

    deleteF(my_data.name)
    
    flash("Employee Deleted Successfully")
 
    return redirect(url_for('teacheradd'))
