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

class CreateUser(TestCase):
    pass


class CreateCouse(TestCase):
    def setUp(self):
        self.client = Client()
        testTAUser = User(id=1, userType="TA", email="testTA@uwm.edu", password="1234")
        testInstructorUser = User(id=2, userType="Instructor", email="testInstructor@uwm.edu", password="1234")
        testAdminUser = User(id=3, userType="Admin", email="testAdminUser@uwm.edu", password="2222")
        testTAUser.save()
        testInstructorUser.save()
        testAdminUser.save()

    def test_CourseCreateWithoutAssignments(self):
        resp = self.client.post("/create-course/", {
            "title": "testtitle", 
            "description": "testdescription", 
            "schedule": "testschedule"
        }, follow=True)
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(resp.context['assignments'], "")  
        # Check that the course details are correctly passed
        self.assertEqual(resp.context['title'], "testtitle")
        self.assertEqual(resp.context['description'], "testdescription")
        self.assertEqual(resp.context['schedule'], "testschedule")
        # Check that the course is actually saved in the database
        course = Class.objects.get(title="testtitle")
        self.assertIsNotNone(course)
        self.assertEqual(course.title, "testtitle")
        self.assertEqual(course.description, "testdescription")
        self.assertEqual(course.schedule, "testschedule")

    def test_CourseCreateWithAssignments(self):
        pass

    def test_EmptyTitle(self):
        pass

    def test_InvalidTitle(self):
        pass

    def test_EmptyDescription(self):
        pass

    def test_InvalidDescription(self):
        pass

    def test_EmptySchedule(self):
        pass

    def test_ValidScheduleStartEndDates(self):
        pass

    def test_ValidSchduleStartDate(self):
        pass

    def test_DuplicateCourse(self):
        pass

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



