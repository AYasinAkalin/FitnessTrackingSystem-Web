#!/usr/bin/env python
# -*- coding: utf-8 -*-

###### LIBRARIES ######
from flask import Flask, render_template, request, session, json, jsonify, redirect, url_for, flash, Markup
import urllib2
from flaskext.mysql import MySQL
from flask_argon2 import Argon2  # Required for Argon2 Encryption
from passlib.hash import sha256_crypt  # Required for SHA2/SHA256 Encryption
from datetime import datetime

###### OBJECTS ######
mysql = MySQL()
app = Flask(__name__)
app.secret_key = "adadaxax"
app.config.from_pyfile("dbconfig.cfg")
mysql.init_app(app)
argon2 = Argon2(app)

# Keys for Google reCaptcha
SITE_KEY = '6LfGDCIUAAAAAAJ17rzeND2i8lRx21UCZxEixwOo'
SECRET_KEY = '6LfGDCIUAAAAAASyHxGV1we8ebkhptgD3TzCFWc4'

modes = ["development", "debug", "release"]
activeMode = modes[0]  # Change to 'release' to activate reChaptcha


@app.route("/")
def hello():
    return render_template("login.html")


# Helper function for Google reCaptcha
def checkRecaptcha(response, secretkey):
    url = 'https://www.google.com/recaptcha/api/siteverify?'
    url = url + 'secret=' + secretkey
    url = url + '&response=' + response
    try:
        jsonobj = json.loads(urllib2.urlopen(url).read())
        if jsonobj['success']:
            return True
        else:
            return False
    except Exception as e:
        print e
        return False


@app.route("/login", methods=["POST"])
def login():
    cursor = mysql.get_db().cursor()
    email = request.form['email']  # formda input fieldda name ne ise onu alır.
    password = request.form['password']

    # Getting hashes
    sql = "SELECT id, name, surname, email, role, hashArgon, hashSHA256 FROM users WHERE email='%s'" % (email)
    cursor.execute(sql)
    response = cursor.fetchone()  # if one value -> fetchone()

    if response:
        hashArgonFromDB = response[5]  # Getting Argon2 hash from database
        hashSHA256FromDB = response[6]  # Getting SHA2/SHA256 hash from database
        # Resolving hashes and generation pass ticket
        ticketArgon = argon2.check_password_hash(hashArgonFromDB, password)
        ticketSHA256 = sha256_crypt.verify(password, hashSHA256FromDB)
        ticket = ticketArgon and ticketSHA256
    else:
        ticket = False
    message = 'Not authorized.'
    category = 'warning'
    link = '/'
    '''Following check is introduced
    because automated tests are not working when recaptcha is enabled.'''
    if activeMode == "release":
        responseRecapthca = request.form.get('g-recaptcha-response')
        check = checkRecaptcha(responseRecapthca, SECRET_KEY)
        if check and ticket:  # Database answered, recaptcha is verified.
            session["user"] = response
            return redirect("/dashboard")
        elif ticket:  # recaptcha is not verified. Possible bot.
            message = "Show us what you got, tissue or metal?"
            flash(message, category)
            return redirect(link)
        else:  # No user is found.
            flash(message, category)
            return redirect(link)
    else:
        if ticket:  # there is a user with given info
            session["user"] = response
            return redirect("/dashboard")
        else:  # No user is found.
            flash(message, category)
            return redirect(link)


@app.route("/dashboard", methods=["GET"])
def dashboard():
    cursor = mysql.get_db().cursor()
    if session["user"][4] == 0:  # user role is admin
        cursor.execute("select name,surname,email,telephone,id from users where role=1")  # get trainers sql
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

        cursor.execute("select users.name,users.surname,messages.msg from messages join users on users.id=messages.traineeid where messages.trainerid=%s"%session["user"][0])
        messages=cursor.fetchall()
        session["messages"]=messages
        return render_template("trainerprofile.html", trainer=session["user"], messages=session["messages"],trainees=session["trainees"], rooms=session["rooms"])
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

        hashArgon2 = argon2.generate_password_hash(password)
        hashSHA256 = sha256_crypt.hash(password)

        cursor = mysql.get_db().cursor()
        sql = "INSERT INTO users(name,surname,email,password,role,telephone, hashArgon, hashSHA256) VALUES('%s','%s','%s',md5('%s'),1,'%s','%s','%s')" % (name, surname, email, password, telephone, hashArgon2, hashSHA256)

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
            telephone = request.form["telephone"]

            weight = request.form["weight"]
            height = request.form["height"]
            additional_info = request.form["info"]

            password = request.form["password"]
            # willPasswordChange = request.form["force-change-pass"]

            hashArgon2 = argon2.generate_password_hash(password)
            hashSHA256 = sha256_crypt.hash(password)

            trainerId = session["user"][0]

            cursor = mysql.get_db().cursor()
            # first insert into users
            sql = "INSERT INTO users(name, surname, email,password, role, telephone, hashArgon, hashSHA256) VALUES('%s','%s','%s',md5('%s'),2,'%s', '%s', '%s')" % (name, surname, email, password, telephone, hashArgon2, hashSHA256)
            cursor.execute(sql)

            user_id = cursor.lastrowid
            sql = "INSERT INTO trainees(id,weight,height,info,trainerId) VALUES('%s','%s','%s','%s',%s)" % (user_id, weight, height, additional_info, trainerId)
            cursor.execute(sql)

            try:
                mysql.get_db().commit()
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
        category = "warning"
        flash(message, category)
        return redirect("/dashboard")


@app.route("/addequipment", methods=["GET", "POST"])
def addequipment():
    if request.method == "GET":
        return render_template("addequipment.html", user=session["user"])
    else:
        name = request.form["name"]
        sql = "INSERT INTO equipments(name) VALUES('%s')" % (name)

        cursor = mysql.get_db().cursor()

        message = "Error occurred."
        category = "error"
        try:
            cursor.execute(sql)
            mysql.get_db().commit()

            message = "Equipment added successfully."
            category = "success"
        except Exception as e:
            raise e
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
        sql = "INSERT INTO rooms(name,number,size) VALUES('%s','%s','%s')" % (name, number, size)
        cursor = mysql.get_db().cursor()

        message = "Error occurred."
        category = "error"
        try:
            cursor.execute(sql)
            mysql.get_db().commit()
            message = "Room added successfully."
            category = "success"
        except Exception as e:
            raise e
        finally:
            flash(message, category)
            return redirect("/dashboard")



@app.route("/addevent", methods=["GET", "POST"])
def add_event():
    if request.method == "GET":
        return render_template("addevent.html", rooms=session["rooms"], user=session["user"])
    else:
        startdate = request.form["starttime"]
        enddate = request.form["endtime"]
        name = request.form["name"]

        cursor = mysql.get_db().cursor()
        room_id = request.form["room"]  # [0] <<- This one makes form to take only one character
        trainer_id = session["user"][0]
        sql = "INSERT INTO events(startdate, enddate, name, trainerid, roomid) VALUES ('%s', '%s', '%s', '%s', '%s')" % (startdate, enddate, name, trainer_id, room_id)

        message = "Error occurred."
        category = "error"
        try:
            cursor.execute(sql)
            mysql.get_db().commit()
            message = "Event added successfully."
            category = "success"
        except Exception as e:
            raise e
        finally:
            flash(message, category)
            return redirect("/dashboard")


@app.route("/addtask", methods=["GET", "POST"])
def add_task():
    if request.method == "GET":
        return render_template("addtask.html", trainees=session["trainees"], user=session["user"])
    else:
        taskName = request.form["taskName"]
        traineeId = request.form["traineeId"]
        info = request.form["info"]
        validdate=request.form["validuntil"]
        sql = "INSERT INTO `tasks`(`taskName`, `traineeId`,`info`, `status`,`validuntil`) VALUES ('%s',%s,'%s',0,'%s')" % (taskName, traineeId, info,validdate)
        cursor = mysql.get_db().cursor()

        try:
            cursor.execute(sql)
            mysql.get_db().commit()
            message = "Task added successfully."
            category = "success"
        except Exception as e:
            raise e
            message = "Error occurred."
            category = "error"
        finally:
            flash(message, category)
            return redirect("/dashboard")


@app.route("/logout",methods=["GET"])
def logout():
    session.clear()
    return redirect("/")


@app.route("/trainerwindow/<int:trainerid>",methods=["GET"])
def trainer_window(trainerid):
    cursor = mysql.get_db().cursor()
    # EVENT DATA PULL FROM DB
    sql = """SELECT * 
             FROM `events`
             WHERE events.trainerid='%s'
                AND events.startdate<CURRENT_DATE + 7
                AND events.startdate>CURRENT_DATE""" % trainerid
    cursor.execute(sql)
    eventsTupleFromDB = cursor.fetchall()
    eventsList = []

    ''' Converting date and time info into simplified form
    Adding room number to eventsTupleFromDB tuple '''
    for event in eventsTupleFromDB:
        eventName = str(event[3])  # Taking name of the event

        startOfEvent = str(event[1])  # Taking and converting start date&time
        endOfEvent = str(event[2])  # Taking and converting end date&time
        i = endOfEvent.find(" ")
        eventStartTime = startOfEvent[(i + 1):(i + 6)]  # Taking only the time
        eventEndTime = endOfEvent[(i + 1):(i + 6)]  # Taking only the time
        if startOfEvent > endOfEvent:
            eventEndTime += " (next day)"  # Adding a message if event ends next day

        startDate = startOfEvent[:i]  # Taking start date of event

        # Sending information imported from tuple to a new tuple
        newEvent = (eventName, startDate, eventStartTime, eventEndTime)

        # Adding room number info to newEvent from database
        roomID = event[5]
        sql = """SELECT `number`
                 FROM `rooms`
                 WHERE rooms.id = '%s' """ % roomID
        cursor.execute(sql)
        newEvent += cursor.fetchone()  # Room number is added

        eventsList.append(newEvent)  # Sending newEvent to eventsList
    # END OF EVENT DATA PULL

    # TRAINEE DATA PULL FROM DB
    sql = """SELECT name, surname, email, telephone
             FROM trainees
                JOIN users ON users.id=trainees.id
             WHERE trainees.trainerId=%s""" % trainerid
    cursor.execute(sql)
    trainer_trainees = cursor.fetchall()
    traineeList = []

    ''' Removing private information from trainee '''
    for trainee in trainer_trainees:
        trainee = list(trainee)  # Convert trainee tuple to list
        trainee[0] += " " + trainee[1]  # Combining first name and surname

        # Hiding some characters of email address
        try:
            index = trainee[2].find("@")
            if index <= 4:
                trainee[2] = trainee[2][0:index] + "*****"
            else:
                trainee[2] = trainee[2][0:4] + "*****"
        except Exception as e:
            raise e

        # Hiding some digits of phone number
        try:
            length = len(trainee[3])
            if length > 4:
                trainee[3] = "****" + trainee[3][(length - 4):length]
            else:
                trainee[3] = "****" + trainee[3]
        except Exception as e:
            raise e

        del trainee[1]  # Removing surname field
        traineeList.append(trainee)
    # END OF TRAINEE DATA PULL

    # TRAINER DATA PULL FROM DB
    sql = """SELECT name, surname, email, telephone, large
             FROM users
                JOIN profilePictures ON profilePictures.id=users.id
             WHERE users.id = '%s'""" % trainerid
    cursor.execute(sql)  # get trainer info
    trainer_info = cursor.fetchone()
    session["trainer"] = trainer_info
    # END OF TRAINER DATA PULL
    return render_template("trainerwindow.html",
                            trainees=traineeList,
                            events=eventsList,
                            trainer=session["trainer"])


# webServices
@app.route("/ws/login", methods=["POST"])
def login_trainee():
    cursor = mysql.get_db().cursor()
    email = request.json["email"]
    password = request.json["password"]

    # Getting hashes
    sql = "SELECT id, name, surname, email, role, hashArgon, hashSHA256 FROM users WHERE email='%s'" % (email)
    cursor.execute(sql)
    response = cursor.fetchone()  # if one value -> fetchone()

    # Resolving hashes and generation pass ticket
    if response:
        role = response[4]
        hashArgonFromDB = response[5]  # Getting Argon2 hash from database
        hashSHA256FromDB = response[6]  # Getting SHA2/SHA256 hash from database
        ticketArgon = argon2.check_password_hash(hashArgonFromDB, password)
        ticketSHA256 = sha256_crypt.verify(password, hashSHA256FromDB)
        ticket = ticketArgon and ticketSHA256
    else:
        ticket = False

    if ticket:
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
    sql = "SELECT id,taskName,info,status,validuntil FROM tasks WHERE traineeId=%d AND  CURRENT_DATE+7 >validuntil" % traineeId
    cursor.execute(sql)
    tasks = cursor.fetchall()

    return jsonify(
        tasks=tasks
    )


@app.route("/ws/events",methods=["GET"])
def mock():
    cursor = mysql.get_db().cursor()
    sql="select * from events"
    cursor.execute(sql)
    return jsonify(
        events=cursor.fetchall()
    )


@app.route("/ws/events/<int:userid>", methods=["GET"])
def get_events(userid):
    cursor = mysql.get_db().cursor()
    sql = """select events.id as eid,startdate,enddate,events.name,
(case when size>(select count(*) from joining where joining.eventid=eid) then 0
when size<=(SELECT COUNT(*) from joining where joining.eventid=eid) then 1
end) as isFull,

(SELECT COUNT(*) from joining where joining.eventid=eid and joining.traineeid=%s) as joins
FROM events ,rooms  WHERE startdate > CURRENT_DATE and enddate< DATE_ADD(CURRENT_DATE,INTERVAL 7 DAY) and rooms.id=events.roomid""" % userid
    cursor.execute(sql)
    events = cursor.fetchall()

    return jsonify(
        events=events
    )


@app.route("/ws/task/<int:taskId>/complete", methods=["GET"])
def complete_task(taskId):
    cursor = mysql.get_db().cursor()
    sql = "update tasks set status=1 where id=%d" % taskId
    cursor.execute(sql)
    mysql.get_db().commit()
    return "OK"


@app.route("/ws/events/join/<int:eventId>/<int:traineeId>",methods=["GET"])
def join_event(eventId,traineeId):
    cursor=mysql.get_db().cursor()
    sql="Insert into joining(eventid,traineeid) values(%s,%s)"%(eventId,traineeId)
    cursor.execute(sql)
    mysql.get_db().commit()
    return "joined"


@app.route("/ws/events/leave/<int:eventId>/<int:traineeId>",methods=["GET"])
def leave_event(eventId,traineeId):
    cursor=mysql.get_db().cursor()
    sql="DELETE FROM joining where eventid=%s and traineeid=%s"%(eventId,traineeId)
    print sql
    cursor.execute(sql)
    mysql.get_db().commit()
    return "left"

@app.route("/ws/messages/gettrainerid/<int:traineeid>", methods=["GET"])
def get_trainerid(traineeid):
    cursor = mysql.get_db().cursor()
    sql = "SELECT trainerId FROM trainees WHERE id =%s"%(traineeid)
    cursor.execute(sql)

    gettrainerid = cursor.fetchall()
    return jsonify(
        gettrainerid = gettrainerid
    )

@app.route("/ws/messages/send",methods=["POST"])
def send_message():
    cursor=mysql.get_db().cursor()
    idd = request.json["id"]
    msg = request.json["msg"]
    trainerId = request.json["trainerid"]
    sql="Insert into messages(trainerid,traineeid,msg) values(%s,%s,'%s')"%(trainerId,idd,msg)

    cursor.execute(sql)
    mysql.get_db().commit()
    return "sent"

@app.route("/ws/equipments", methods=["GET"])
def get_equipments():
    cursor = mysql.get_db().cursor()
    sql = "select * from equipments"
    cursor.execute(sql)

    equipments = cursor.fetchall()
    return jsonify(
        equipments = equipments
    )


@app.route("/ws/equipments/use/<int:equipmentId>/<int:traineeId>", methods=["GET"])
def use_equipment(equipmentId, traineeId):
    cursor = mysql.get_db().cursor()
    sql = "update equipments set status=%s where id=%s"%(traineeId, equipmentId)
    cursor.execute(sql)
    mysql.get_db().commit()
    return "OK"


@app.route("/ws/equipments/release/<int:equipmentId>/<int:traineeId>", methods=["GET"])
def release_equipment(equipmentId, traineeId):
    cursor = mysql.get_db().cursor()
    sql = "update equipments set status=0 where id=%s and status=%s"%(equipmentId, traineeId)
    cursor.execute(sql)
    mysql.get_db().commit()
    return "OK"


if __name__ == "__main__":
    app.run()
