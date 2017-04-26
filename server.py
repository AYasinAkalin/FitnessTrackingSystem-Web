#!/usr/bin/env python   
# -*- coding: utf-8 -*-

from flask import Flask,render_template,request,session
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
        role=response[4]        
        if role==0: #the user is admin
            cursor.execute("select name,surname,email,telephone from users where role=1") #get trainers sql
            trainers=cursor.fetchall()#if multiple values -> fetchall()
            session["user"]=response
            session["trainers"]=trainers
            return render_template("adminprofile.html",admin=response,trainers=trainers)
        elif role==1: #the user is trainer

            cursor.execute("select id,name,surname from trainees ") # get trainees sql
            trainees = cursor.fetchall()
            session["user"] = response
            session["trainees"] = trainees
            return render_template("trainerprofile.html" , trainer = response , trainees = trainees)

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
        print sql
        cursor.execute(sql)
        mysql.get_db().commit()
        
        cursor.execute("select name,surname,email,telephone from users where role=1") #get trainers sql
        trainers=cursor.fetchall()
        session["trainers"]=trainers
    return render_template("adminprofile.html",admin=session["user"],trainers=session["trainers"])

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
        cursor=mysql.get_db().cursor()
        sql="Insert into trainees(name,surname,email,telephone,weight,height,info) values('%s','%s','%s','%s',%s,%s,'%s')" %(name,surname,email,telephone,weight,height,additional_info)
        print sql
        cursor.execute(sql)
        mysql.get_db().commit()
        
        cursor.execute("select id,name,surname from trainees") #get trainees sql
        trainers=cursor.fetchall()
        session["trainees"]=trainees
    return render_template("trainerprofile.html",trainers=session["user"],trainees=session["trainees"])

def add_program() :
    pass

def add_event() :
    pass


if __name__ == "__main__":
    app.run()