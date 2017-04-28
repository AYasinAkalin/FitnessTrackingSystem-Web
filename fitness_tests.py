import unittest
import server

class FitnessTestCase(unittest.TestCase):

    def setUp(self):
        self.app=server.app.test_client()

    def test_server(self):
        rv=self.app.get("/")
        assert rv.status_code==200
    
    def test_login(self):
        rv=self.app.post("/login",data=dict(
            email="admin@fitness.com",
            password="adminpass"
        ))
        assert "dashboard" in rv.data

    
if __name__=="__main__":
    unittest.main()