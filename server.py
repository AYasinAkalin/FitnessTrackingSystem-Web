#!/usr/bin/env python   
# -*- coding: utf-8 -*-

from flask import Flask,render_template,request,session,json ,jsonify ,redirect,url_for
from flaskext.mysql import MySQL
mysql=MySQL()
app = Flask(__name__)
app.secret_key = "adadaxax"
app.config.from_pyfile("dbconfig.cfg")
mysql.init_app(app)


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
        

@app.route("/dashboard",methods=["GET"])
def dashboard():
    cursor=mysql.get_db().cursor()
    if session["user"][4]==0: #user role is admin
        cursor.execute("select name,surname,email,telephone from users where role=1") #get trainers sql
        trainers=cursor.fetchall()#if multiple values -> fetchall()
        session["trainers"]=trainers
        return render_template("adminprofile.html",admin=session["user"],trainers=session["trainers"])
    elif session["user"][4]==1: #user role is trainer
        cursor.execute("select id,name,surname,weight,height from trainees where trainerId=%s"%session["user"][0]) #my user id
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
        sql="Insert into trainees(name,surname,email,telephone,weight,height,info,trainerId) values('%s','%s','%s','%s','%s','%s','%s',%s)" %(name,surname,email,telephone,weight,height,additional_info,trainerId)
        
        cursor.execute(sql)
        mysql.get_db().commit()
        
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
        return redirect("dashboard")

@app.route("/addtask",methods=["POST"])
def add_task():
    taskName=request.form["taskName"]
    traineeId=request.form["traineeId"]
    info=request.form["info"]
    sql="INSERT INTO `tasks`(`taskName`, `traineeId`,`info`, `status`) VALUES ('%s',%s,'%s',0)" %(taskName,traineeId,info)
    cursor=mysql.get_db().cursor()
    cursor.execute(sql)
    mysql.get_db().commit()
    return redirect("/dashboard")

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
    sql="select id,taskName,status from tasks where traineeId=%d" % traineeId
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