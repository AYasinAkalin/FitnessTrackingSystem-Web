#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, session, json, jsonify, redirect, url_for, flash, Markup

from flaskext.mysql import MySQL
mysql = MySQL()
app = Flask(__name__)
app.secret_key = "adadaxax"
app.config.from_pyfile("dbconfig.cfg")
mysql.init_app(app)


@app.route("/")
def hello():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    cursor = mysql.get_db().cursor()
    email = request.form['email']  # formda input fieldda name ne ise onu alır.
    password = request.form['password']
    sql = "select id,name,surname,email,role from users where email='%s' and password='%s'" % (email, password)
    cursor.execute(sql)
    response = cursor.fetchone()  # if one value -> fetchone()

    if response:  # there is a user with given info
        session["user"] = response
        return redirect("/dashboard")
    else:
        message = "Not authorized."
        category = "warning"
        flash(message, category)
        return redirect("/")


@app.route("/dashboard", methods=["GET"])
def dashboard():
    cursor = mysql.get_db().cursor()
    if session["user"][4] == 0:  # user role is admin
        cursor.execute("select name,surname,email,telephone from users where role=1")  # get trainers sql
        trainers = cursor.fetchall()  # if multiple values -> fetchall()
        session["trainers"] = trainers

        cursor.execute("select * from users where role=2")  # get trainees sql for counting purpose
        trainees = cursor.fetchall()  # if multiple values -> fetchall()
        session["trainees"] = trainees

        cursor.execute("select name from equipments")
        equipments = cursor.fetchall()
        session["equipments"] = equipments

        cursor.execute("select name,number,size from rooms")
        rooms = cursor.fetchall()
        session["rooms"] = rooms

        return render_template("adminprofile.html", 
                                admin=session["user"], 
                                trainers=session["trainers"], trainees=session["trainees"],
                                equipments=session["equipments"], rooms=session["rooms"])
    elif session["user"][4] == 1:  # user role is trainer
        cursor.execute("select users.id,name,surname,email,telephone,weight,height,info from users join trainees on users.id=trainees.id where trainees.trainerId=%s" % session["user"][0])  # my user id
        trainees = cursor.fetchall()
        session["trainees"] = trainees

        cursor.execute("select * from rooms")
        rooms = cursor.fetchall()
        session["rooms"] = rooms

        return render_template("trainerprofile.html", trainer=session["user"], trainees=session["trainees"], rooms=session["rooms"])
    else:  # user role is trainee
        return "You are a trainee. Please use mobile."


@app.route("/addtrainer", methods=["GET", "POST"])
def addtrainer():
    if request.method == 'GET':
        return render_template("addtrainer.html", user=session["user"])
    else:
        # isAdmin = request.form["admin-checkbox"]
        # isTrainer = request.form["trainer-checkbox"]
        # isTrainee = request.form["trainee-checkbox"]

        name = request.form["firstname"]
        surname = request.form["lastname"]
        email = request.form["email"]
        telephone = request.form["telephone"]

        password = request.form["password"]
        # willPasswordChange = request.form["force-change-pass"]

        cursor = mysql.get_db().cursor()
        sql = "Insert into users(name,surname,email,password,role,telephone) values('%s','%s','%s','%s',1,'%s')" % (name, surname, email, password, telephone)

        try:
            cursor.execute(sql)
            mysql.get_db().commit()
            message = "Trainer added successfully."
            category = "success"
        except Exception as e:
            raise e
            message = "Error occurred."
            category = "error"
        finally:
            flash(message, category)
            return redirect("/dashboard")


@app.route("/addtrainee", methods=["GET", "POST"])
def addtrainee():
    cursor = mysql.get_db().cursor()
    if session["user"][4] == 1:  # user role is trainer
        if request.method == 'GET':
            return render_template("addtrainee.html", user=session["user"])
        else:
            # isTrainee = request.form["trainee-checkbox"]
            name = request.form["firstname"]
            surname = request.form["lastname"]
            email = request.form["email"]
            password = request.form["password"]
            # willPasswordChange = request.form["force-change-pass"]
            telephone = request.form["telephone"]
            weight = request.form["weight"]
            height = request.form["height"]
            additional_info = request.form["info"]
            trainerId = session["user"][0]
            cursor = mysql.get_db().cursor()
            # first insert into users
            sql = "Insert into users(name,surname,email,password,role,telephone) values('%s','%s','%s','%s',1,'%s')" % (name, surname, email, password, telephone)
            cursor.execute(sql)

            user_id = cursor.lastrowid
            sql = "Insert into trainees(id,weight,height,info,trainerId) values('%s','%s','%s','%s',%s)" % (user_id, weight, height, additional_info, trainerId)
            cursor.execute(sql)

            try:
                mysql.get_db().commit()
                # Example markup message
                '''message = Markup("<h1>Voila! Room is added.</h1>")'''
                message = "Trainee added successfully."
                category = "success"
            except Exception as e:
                raise e
                message = "Error occurred."
                category = "error"
            finally:
                flash(message, category)
                return redirect("/dashboard")

    else:
        message = Markup("You can not add any trainee from administrator panel.")
        ''' Other categories are:
            "success", "error", "info", "warning"
        '''
        category = "warning"
        flash(message, category)
        return redirect("/dashboard")


@app.route("/addequipment", methods=["GET", "POST"])
def addequipment():
    if request.method == "GET":
        return render_template("addequipment.html", user=session["user"])
    else:
        name = request.form["name"]
        sql = "Insert into equipments(name) values('%s')" % (name)
        print sql
        cursor = mysql.get_db().cursor()

        try:
            cursor.execute(sql)
            mysql.get_db().commit()
            # Example markup message
            '''message = Markup("<h1>Voila! Room is added.</h1>")'''
            message = "Equipment added successfully."
            category = "success"
        except Exception as e:
            raise e
            message = "Error occurred."
            category = "error"
        finally:
            flash(message, category)
            return redirect("/dashboard")


@app.route("/addroom", methods=["GET", "POST"])
def addroom():
    if request.method == "GET":
        return render_template("addroom.html", user=session["user"])
    else:
        name = request.form["name"]
        number = request.form["number"]
        size = request.form["size"]
        sql = "Insert into rooms(name,number,size) values('%s','%s','%s')" % (name, number, size)
        cursor = mysql.get_db().cursor()

        try:
            cursor.execute(sql)
            mysql.get_db().commit()
            # Example markup message
            '''message = Markup("<h1>Voila! Room is added.</h1>")'''
            message = "Room added successfully."
            category = "success"
        except Exception as e:
            raise e
            message = "Error occurred."
            category = "error"
        finally:
            flash(message, category)
            return redirect("/dashboard")


def add_program():
    pass


@app.route("/addevent", methods=["GET", "POST"])
def add_event():
    if request.method == "GET":
        return render_template("addevent.html", rooms=session["rooms"])
    else:
        year = request.form["year"]
        month = request.form["month"]
        day = request.form["day"]
        starttime = request.form["starttime"]
        endtime = request.form["endtime"]
        name = request.form["name"]
        startdate = "%s-%s-%s %s" % (year, month, day, starttime)
        enddate = "%s-%s-%s %s" % (year, month, day, endtime)
        cursor = mysql.get_db().cursor()
        room_id = request.form["room"]  # [0] <<- This one makes form to take only one character
        trainer_id = session["user"][0]
        # TODO: Add Room ID to SQL statement just below
        sql = "INSERT INTO events(startdate, enddate, name, trainerid, roomid) VALUES ('%s', '%s', '%s', '%s', '%s')" % (startdate, enddate, name, trainer_id, room_id)
        print sql
        cursor.execute(sql)
        mysql.get_db().commit()
        print year, month, day, starttime, endtime, name, room_id
        message = "Event added successfully."
        category = "success"
        flash(message, category)
        return redirect("dashboard")


@app.route("/addtask", methods=["GET", "POST"])
def add_task():
    if request.method == "GET":
        return render_template("addtask.html", trainees=session["trainees"], user=session["user"])
    else:
        taskName = request.form["taskName"]
        traineeId = request.form["traineeId"]
        info = request.form["info"]
        sql = "INSERT INTO `tasks`(`taskName`, `traineeId`,`info`, `status`) VALUES ('%s',%s,'%s',0)" % (taskName, traineeId, info)
        cursor = mysql.get_db().cursor()

        try:
            cursor.execute(sql)
            mysql.get_db().commit()
            # Example markup message
            '''message = Markup("<h1>Voila! Room is added.</h1>")'''
            message = "Task added successfully."
            category = "success"
        except Exception as e:
            raise e
            message = "Error occurred."
            category = "error"
        finally:
            flash(message, category)
            return redirect("/dashboard")

# webServices
@app.route("/ws/login", methods=["POST"])
def login_trainee():
    email = request.json["email"]
    password = request.json["password"]
    cursor = mysql.get_db().cursor()
    sql = "select id,name,surname,email,role from users where email='%s' and password='%s'" % (email, password)
    cursor.execute(sql)
    response = cursor.fetchone()  # if one value -> fetchone()

    if response:
        role = response[4]
        if role == 2:
            return jsonify(
                response="OK",
                user=response
            )
        else:
            return jsonify(
                response="NT"  # not trainer
            )
    else:
        return jsonify(
            response="NA"  # not admin
        )


@app.route("/ws/tasks/<int:traineeId>", methods=["GET"])
def get_tasks(traineeId):
    cursor = mysql.get_db().cursor()
    sql = "select id,taskName,info,status from tasks where traineeId=%d" % traineeId
    cursor.execute(sql)
    tasks = cursor.fetchall()

    return jsonify(
        tasks=tasks
    )

@app.route("/ws/events", methods=["GET"])
def get_events():
    cursor = mysql.get_db().cursor()
    sql = "select * FROM events WHERE startdate > CURRENT_DATE"
    cursor.execute(sql)
    events = cursor.fetchall()

    return jsonify(
        events = events
    )

@app.route("/ws/task/<int:taskId>/complete", methods=["GET"])
def complete_task(taskId):
    cursor = mysql.get_db().cursor()
    sql = "update tasks set status=1 where id=%d" % taskId
    cursor.execute(sql)
    mysql.get_db().commit()
    return "OK"

if __name__ == "__main__":
    app.run()
