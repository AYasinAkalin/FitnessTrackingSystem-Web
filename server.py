#!/usr/bin/env python   
# -*- coding: utf-8 -*-

from flask import Flask,render_template,request,session,json ,jsonify ,redirect,url_for,flash,Markup
# Markup added above to pass good looking messages to flash. -AY

from flaskext.mysql import MySQL
mysql=MySQL()
app = Flask(__name__)
app.secret_key = "adadaxax"
app.config.from_pyfile("dbconfig.cfg")
mysql.init_app(app)

#TODO: add flash thing
    # Half-way solution:
    # We need to add one of the following "flashes" class to html file but I don't exactly know where to, to make it work properly -AY
""" This one for simple messages.
    <div class="flashes">
        {% for message in get_flashed_messages()%}
            {{ message | safe}} <!--# "...|safe" is needed to pass HTML code but opens a backdoor to XSS attacks. -AY-->
        {% endfor %}
    </div>
"""

""" This one uses Bootstrap message boxes.
    <div class="flashes">
        {% with messages = get_flashed_messages(with_categories=true) %}
        <!-- Categories: success (green), info (blue), warning (yellow), danger (red) -->
        {% if messages %}
            {% for category, message in messages %}
            <div class="alert alert-{{ category }} alert-dismissible" role="alert">
            <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <!-- <strong>Title</strong> --> {{ message }}
            </div>
            {% endfor %}
        {% endif %}
        {% endwith %}
    </div>
"""  

@app.route("/")
def hello():
    return render_template("login.html")


@app.route("/login",methods=["POST"])
def login():
    cursor=mysql.get_db().cursor()
    email=request.form['email'] #formda input fieldda name ne ise onu alır.
    password=request.form['password']
    sql="select id,name,surname,email,role from users where email='%s' and password='%s'" %(email,password)
    cursor.execute(sql)
    response=cursor.fetchone() #  if one value -> fetchone()
    
    if response: # there is a user with given info
        session["user"]=response
        return redirect("/dashboard")
    else:
        return "Not authorized"

@app.route("/dashboard",methods=["GET"])
def dashboard():
    cursor=mysql.get_db().cursor()
    if session["user"][4]==0: #user role is admin
        cursor.execute("select name,surname,email,telephone from users where role=1") #get trainers sql
        trainers=cursor.fetchall()#if multiple values -> fetchall()
        session["trainers"]=trainers
        cursor.execute("select name from equipments")
        equipments = cursor.fetchall()
        session["equipments"] = equipments 
        return render_template("adminprofile.html",admin=session["user"],trainers=session["trainers"] , equipments=session["equipments"])
    elif session["user"][4]==1: #user role is trainer
        cursor.execute("select users.id,name,surname,email,telephone,weight,height,info from users join trainees on users.id=trainees.id where trainees.trainerId=%s"%session["user"][0]) #my user id
        trainees=cursor.fetchall()
        session["trainees"]=trainees
        return render_template("trainerprofile.html" , trainer = session["user"] , trainees = session["trainees"])
        

    else: #user role is trainee
        return "You are a trainee. Please use mobile."

@app.route("/addtrainer",methods=["GET","POST"])
def addtrainer():
    if request.method=='GET':
        return render_template("addtrainer.html")
    else:
        name=request.form["name"]
        surname=request.form["surname"]
        email=request.form["email"]
        password=request.form["password"]
        telephone=request.form["telephone"]
        cursor=mysql.get_db().cursor()
        sql="Insert into users(name,surname,email,password,role,telephone) values('%s','%s','%s','%s',1,'%s')" %(name,surname,email,password,telephone)
      
        cursor.execute(sql)
        mysql.get_db().commit()
    
        return redirect("/dashboard")

@app.route("/addtrainee",methods=["GET","POST"])
def addtrainee():
    if request.method=='GET':
        return render_template("addtrainee.html")
    else:
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        password = request.form["password"]
        telephone = request.form["telephone"]
        weight = request.form["weight"]
        height = request.form["height"]
        additional_info = request.form["info"]
        trainerId=session["user"][0]
        cursor=mysql.get_db().cursor()
        #first insert into users
        sql="Insert into users(name,surname,email,password,role,telephone) values('%s','%s','%s','%s',1,'%s')" %(name,surname,email,password,telephone)
        cursor.execute(sql)
       
        user_id=cursor.lastrowid
        sql="Insert into trainees(id,weight,height,info,trainerId) values('%s','%s','%s','%s',%s)" %(user_id,weight,height,additional_info,trainerId)
        
        cursor.execute(sql)
        mysql.get_db().commit()
        
        return redirect("/dashboard")

@app.route("/addequipment",methods=["GET","POST"]) 
def addequipment() :
    if request.method == "GET" :
        return render_template("addequipment.html")
    else :
        name = request.form["name"]
        sql = "Insert into equipments(name) values('%s')" %(name)
        print sql
        cursor=mysql.get_db().cursor()
        cursor.execute(sql)
        mysql.get_db().commit()
        print name
        return redirect("/dashboard")

@app.route("/addroom",methods=["GET","POST"]) 
def addroom() :
    if request.method == "GET" :
        return render_template("addroom.html")
    else :
        name = request.form["name"]
        number = request.form["number"]
        size = request.form["size"]
        sql = "Insert into rooms(name,number,size) values('%s','%s','%s')" %(name,number,size)
        print sql
        cursor=mysql.get_db().cursor()

        cursor.execute(sql)
        mysql.get_db().commit()
        print size, name
        message = "Room added succesfully."
        #messageHTML = "<div class=\"alert alert-success\"> Success! Room added. </div>"
        flash(message)
        return redirect("/dashboard")

def add_program() :
    pass

@app.route("/addevent",methods=["GET","POST"])
def add_event() :
    if request.method == "GET" :
        return render_template("addevent.html")
    else :
        year = request.form["year"]
        month = request.form["month"]
        day = request.form["day"]
        starttime = request.form["starttime"]
        endtime = request.form["endtime"]
        name = request.form["name"]
        startdate = "%s-%s-%s %s"%(year,month,day,starttime)
        enddate = "%s-%s-%s %s"%(year,month,day,endtime)
        cursor=mysql.get_db().cursor()
        trainer_id = session["user"][0]
        sql="Insert into events(startdate,enddate,name,trainerid) values('%s','%s','%s',%s)" %(startdate,enddate,name,trainer_id)
        print sql
        cursor.execute(sql)
        mysql.get_db().commit()
        print year , month , day , starttime , endtime , name 
        return redirect("dashboard") #change to "/dashboard" ??

@app.route("/addtask",methods=["GET","POST"])
def add_task():
    if request.method=="GET":
        return render_template("addtask.html",trainees=session["trainees"])
    else:
        taskName=request.form["taskName"]
        traineeId=request.form["traineeId"]
        info=request.form["info"]
        sql="INSERT INTO `tasks`(`taskName`, `traineeId`,`info`, `status`) VALUES ('%s',%s,'%s',0)" %(taskName,traineeId,info)
        cursor=mysql.get_db().cursor()
        cursor.execute(sql)
        mysql.get_db().commit()
        flash("Task added succesfully")
        return redirect("dashboard") #change to "/dashboard" ??

#webServices
@app.route("/ws/login",methods=["POST"])
def login_trainee():
    email=request.json["email"]
    password=request.json["password"]
    cursor=mysql.get_db().cursor()
    sql="select id,name,surname,email,role from users where email='%s' and password='%s'" %(email,password)
    cursor.execute(sql)
    response=cursor.fetchone() #  if one value -> fetchone()
    
    if response:
        role=response[4]
        if role==2:
            return jsonify(
                response="OK",
                user=response
            ) 
        else:
            return jsonify(
                response="NT" #not trainer
            )
    else:
        return jsonify(
            response="NA" #not admin
        )

@app.route("/ws/tasks/<int:traineeId>",methods=["GET"])
def get_tasks(traineeId):
    cursor=mysql.get_db().cursor()
    sql="select id,taskName,info,status from tasks where traineeId=%d" % traineeId
    cursor.execute(sql)
    tasks=cursor.fetchall()

    return jsonify(
        tasks=tasks
    )

@app.route("/ws/task/<int:taskId>/complete",methods=["GET"])
def complete_task(taskId):
    cursor=mysql.get_db().cursor()
    sql="update tasks set status=1 where id=%d" %taskId
    cursor.execute(sql)
    mysql.get_db().commit()
    return "OK"
   
if __name__ == "__main__":
    app.run()