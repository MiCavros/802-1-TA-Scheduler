from django.test import TestCase, Client
from .models import User, userPublicInfo, userPrivateInfo, Class, Section

class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        testUser = User(id=1, email="testUser@uwm.edu", password="1234")
        testUser.save()

    def test_wrongPassword(self):
        resp = self.client.post("/",{"email": "testUser@uwm.edu","password": "2222"},follow=True)
        self.assertEqual(resp.context["message"],"Incorrect Password")
        self.assertEqual(resp.status_code,200)

    def test_noUser(self):
        resp = self.client.post("/",{"email": "unknownUser@uwm.edu","password": "2222"},follow=True)
        self.assertEqual(resp.context["message"], "No User with this Email")
        self.assertEqual(resp.status_code, 200)

    def test_loginSuccessful(self):
        resp = self.client.post("/",{"email": "testUser@uwm.edu","password": "1234"},follow=True)
        self.assertRedirects(resp, "/home/")
        self.assertEqual(resp.status_code,200)

    def test_BlankEntry(self):
        resp = self.client.post("/",{"email": "","password": ""},follow=True)
        self.assertEqual(resp.context["message"],"Email and/or Password cannot be blank")
        self.assertEqual(resp.status_code,200)

class HomeTest(TestCase):
    def setUp(self):
        self.client = Client()
        testUser = User(id=1, userType="TA", email="testUser@uwm.edu", password="1234")
        testAdminUser = User(id=2, userType="Admin", email="testAdminUser@uwm.edu", password="2222")
        testUser.save()
        testAdminUser.save()

    def test_AdminLogin(self):
        resp = self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        self.assertRedirects(resp, "/home/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["userType"], "Admin")

    def test_UserLogin(self):
        resp = self.client.post("/", {"email": "testUser@uwm.edu", "password": "1234"}, follow=True)
        self.assertRedirects(resp, "/home/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["userType"], "TA")