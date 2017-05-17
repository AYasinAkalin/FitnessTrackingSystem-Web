import unittest
import server
from flask import json
from coverage import coverage
import os
cov = coverage(branch=True, omit=['venv/*', 'fitness_tests.py'])
cov.start()


class FitnessTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
# TODO: update tests to use flash

    def test_admin_login(self):
        rv = self.app.post("/login", data=dict(
            email="admin@fitness.com",
            password="adminpass"
        ), follow_redirects=True)
        assert "dashboard" in rv.data

    def test_trainer_login(self):
        rv = self.app.post("/login", data=dict(
            email="trainer@1.com",
            password="asd"
        ), follow_redirects=True)
        assert "dashboard" in rv.data

    def test_server(self):
        rv = self.app.get("/")
        assert rv.status_code == 200

    def test_add_trainer(self):
        self.test_admin_login()
        rv = self.app.post("/addtrainer", data=dict(
            firstname="testtrainer",
            lastname="testsurname",
            email="testmail@mail",
            password="testpass",
            telephone="123123"
        ), follow_redirects=True)
        assert "dashboard" in rv.data

    def test_add_trainee(self):
        self.test_trainer_login()
        rv = self.app.post("/addtrainee", data=dict(
            firstname="testtrainee",
            lastname="testtraineesurname",
            email="test@trainee",
            password="testpass",
            telephone="1213123",
            weight="50",
            height="50",
            info="testinfo"
        ), follow_redirects=True)
        assert rv.status_code == 200

    def test_add_task(self):

        self.test_trainer_login()
        rv = self.app.post("/addtask", data=dict(
            taskName="testTask",
            traineeId=10,

            info="testinfo"
            ))
        assert "dashboard" in rv.data

    def test_web_login(self):
        rv = self.app.post("/ws/login", data=json.dumps(dict(
            email="berke@berke",
            password="berke"
            )),
            content_type="application/json")
        data = json.loads(rv.data)
        assert data["response"] == "OK"  # authenticated trainee

        rv = self.app.post("/ws/login", data=json.dumps(dict(
            email="admin@fitness.com",
            password="adminpass"
            )),
            content_type="application/json")
        data = json.loads(rv.data)

        assert data["response"] == "NT"  # authenticated user with different role

        rv = self.app.post("/ws/login", data=json.dumps(dict(
            email="wrongmail",
            password="wrongpass"
            )),
            content_type="application/json")
        data = json.loads(rv.data)

        assert data["response"] == "NA"  # not authenticated user

    def test_web_get_tasks(self):
        rv = self.app.get("/ws/tasks/531")
        tasks = json.loads(rv.data)
        assert tasks["tasks"][0][1] == "mytask1"

    def test_web_complete_task(self):
        rv = self.app.get("/ws/task/1/complete")

        assert rv.data == "OK"

if __name__ == "__main__":
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
