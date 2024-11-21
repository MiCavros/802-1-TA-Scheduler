from django.shortcuts import redirect
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

class createUserTest(TestCase):
    def setUp(self):
        self.client = Client()
        testUser = User(id=1, userType="TA", email="testUser@uwm.edu", password="1234")
        testAdminUser = User(id=2, userType="Admin", email="testAdminUser@uwm.edu", password="2222")
        testUser.save()
        testAdminUser.save()

    def test_taAccess(self):
        self.client.post("/", {"email": "testUser@uwm.edu", "password": "1234"}, follow=True)
        resp = self.client.get("/createuser/", follow=True)
        self.assertEqual(resp.context["userType"], "TA")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User Cannot Access This Page")

    def test_adminAccess(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.get("/createuser/", follow=True)
        self.assertEqual(resp.context["userType"], "Admin")
        self.assertEqual(resp.status_code, 200)

    def test_createUserSuccessfully(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createuser/", {"role": "TA", "email": "newTestUser@uwm.edu", "password": "4444"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        newUser = User.objects.get(email="newTestUser@uwm.edu")
        self.assertEqual(newUser.role, "TA")
        self.assertEqual(newUser.password, "4444")

    def test_invalidEmail(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createuser/", {"role": "TA", "email": "newTestUser", "password": "4444"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Invalid Email")

    def test_NoEmail(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createuser/", {"role": "TA", "email": "", "password": "4444"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Email is a required field")

    def test_NoPassword(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createuser/", {"role": "TA", "email": "newTestUser", "password": ""}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Password is a required field")

    def test_noRole(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createuser/", {"email": "newTestUser@uwm.edu", "password": "4321", "role": ""}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Role is a required field")



