import unittest
import server
from flask import json
from coverage import coverage
import os
cov = coverage(branch=True, omit=['venv/*', 'fitness_tests.py'])
cov.start()
class FitnessTestCase(unittest.TestCase):

    def setUp(self):
        self.app=server.app.test_client()
        
        
    def test_admin_login(self):
        rv=self.app.post("/login",data=dict(
            email="admin@fitness.com",
            password="adminpass"
        ),follow_redirects=True)
        assert "dashboard" in rv.data

    def test_not_authorized_login(self):
        rv=self.app.post("/login",data=dict(
            email="no_email",
            password="wrongpass"
        ),follow_redirects=True)

        assert "Not authorized" in rv.data

    def test_trainee_login(self):
        rv=self.app.post("/login",data=dict(
            email="berke@berke",
            password="berke"   
        ),follow_redirects=True)

        assert "mobile" in rv.data

    def test_trainer_login(self):
        rv=self.app.post("/login",data=dict(
            email="trainer@1.com",
            password="asd"
        ),follow_redirects=True)
        assert "dashboard" in rv.data


        
    def test_add_equipment(self):
        self.test_trainer_login()
        rv = self.app.post("/addequipment", data = dict(
            name = "testequipment"
            ) , follow_redirects = True)
        assert "dashboard" in rv.data

        rv = self.app.get("/addequipment")
        assert rv.status_code == 200

   
    def test_add_event(self):
        self.test_trainer_login()
        rv = self.app.post("/addevent" , data = dict(
            year = "2020" ,
            month = "1" ,
            day = "1" ,
            starttime = "12:00" ,
            endtime = "13:00" ,
            name = "testevent",
            room = "10"
            ) , follow_redirects = True)
        assert "dashboard" in rv.data

        rv = self.app.get("/addevent")
        assert rv.status_code == 200
    def test_server(self):
        rv=self.app.get("/")
        assert rv.status_code==200

    def test_add_trainer(self):
        self.test_admin_login()
        rv=self.app.post("/addtrainer",data=dict(
            name="testtrainer",
        surname="testsurname",
        email="testmail@mail",
        password="testpass",
        telephone="123123"
        ),follow_redirects=True)
        assert "dashboard" in rv.data

        rv=self.app.get("/addtrainer")
        assert rv.status_code==200

    def test_add_trainee(self):
        self.test_trainer_login()
        rv=self.app.post("/addtrainee",data=dict(
             name = "testtrainee",
        surname = "testtraineesurname",
        email = "test@trainee",
        password = "testpass",
        telephone = "1213123",
        weight = "50",
        height = "50",
        info = "testinfo"
        ),follow_redirects=True)
        assert rv.status_code==200

        rv=self.app.get("/addtrainee")
        assert rv.status_code==200


    def test_add_task(self):

        self.test_trainer_login()
        rv=self.app.post("/addtask",data=dict(
            taskName="testTask",
            traineeId=10,
       
            info="testinfo"
        ))
        assert "dashboard" in rv.data

        rv=self.app.get("/addtask")
        assert rv.status_code==200

    def test_web_login(self):
        rv=self.app.post("/ws/login",
        data=json.dumps(dict(
            email="berke@berke",
            password="berke"
        )),
        content_type="application/json")
        data=json.loads(rv.data)
        assert data["response"]=="OK" #authenticated trainee

        rv=self.app.post("/ws/login",
        data=json.dumps(dict(
            email="admin@fitness.com",
            password="adminpass"
        )),
        content_type="application/json")
        data=json.loads(rv.data)

        assert data["response"]=="NT" #authenticated user with different role
        

        rv=self.app.post("/ws/login",
        data=json.dumps(dict(
            email="wrongmail",
            password="wrongpass"
        )),
        content_type="application/json")
        data=json.loads(rv.data)

        assert data["response"]=="NA" #not authenticated user

    
    def test_web_get_tasks(self):
        rv=self.app.get("/ws/tasks/531")
        tasks=json.loads(rv.data)
        assert tasks["tasks"][0][1]=="mytask1"

    def test_web_complete_task(self):
        rv=self.app.get("/ws/task/1/complete")
       
        assert rv.data=="OK"
        
    
if __name__=="__main__":
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    print("HTML version: " + os.path.join(".", "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
