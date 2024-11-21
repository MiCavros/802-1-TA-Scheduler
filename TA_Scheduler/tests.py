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


class CreateCourse(TestCase):
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

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['assignments'], "")  

        course = Class.objects.get(title="testtitle")
        self.assertIsNotNone(course)
        self.assertEqual(course.title, "testtitle")
        self.assertEqual(course.description, "testdescription")
        self.assertEqual(course.schedule, "testschedule")

    def test_CourseCreateWithAssignments(self):
        resp = self.client.post("/create-course/", { 
            "title": "testtitle",
            "description": "testdescription", 
            "schedule": "testschedule", 
            "assignments": "testassignments"
        }, follow=True)
        
        self.assertEqual(resp.status_code, 200)

        course = Class.objects.get(title="testtitle")
        self.assertIsNotNone(course)
        self.assertEqual(course.title, "testtitle")
        self.assertEqual(course.description, "testdescription")
        self.assertEqual(course.schedule, "testschedule")
        self.assertEqual(course.assignments, "testassignments")

    def test_EmptyTitle(self):
        resp = self.client.post("/create-course/", {
            "title": "",
            "description": "testdescription",
            "schedule": "testschedule"
        }, follow=True)  
        
        self.assertEqual(resp.status_code, 400) 
        self.assertIn("Title cannot be empty", resp.context['errors'])

    def test_InvalidTitle(self):
        resp = self.client.post("/create-course/", {
            "title": "t" * 51,
            "description": "testdescription", 
            "schedule": "testschedule"
        }, follow=True)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Title exceeds maximum length", resp.context['errors'])

    def test_EmptyDescription(self):
        resp = self.client.post("/create-course/", { 
            "title": "testtitle",
            "description": "", 
            "schedule": "testschedule", 
        }, follow=True)

        self.assertEqual(resp.status_code, 400) 
        self.assertIn("Description cannot be empty", resp.context['errors'])

    def test_InvalidDescription(self):
        resp = self.client.post("/create-course/", {
            "title": "testtitle", 
            "description": "d" * 1001,
            "schedule": "testschedule"
        }, follow=True)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Description exceeds maximum length", resp.context['errors'])

    def test_EmptySchedule(self):    
        resp = self.client.post("/create-course/", {
            "title": "testtitle",
            "description": "testdescription",
            "schedule": "",
            }, follow=True)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Schedule cannot be empty", resp.context['errors'])

    def test_InvalidScheduleStartEndDates(self):
        resp = self.client.post("/create-course/", { 
            "title": "testtitle",
            "description": "", 
            "schedule": "Start Date: 012/01/2024, End Date: 11/20/2024", 
        }, follow=True)

        self.assertEqual(resp.status_code, 400) 
        self.assertIn("Class cannot start after its end date.", resp.context['errors'])

    def test_InvalidSchduleStartDate(self):
        resp = self.client.post("/create-course/", { 
            "title": "testtitle",
            "description": "", 
            "schedule": "Start Date: 01/01/2024, End Date: 01/01/2025", 
        }, follow=True)

        self.assertEqual(resp.status_code, 400) 
        self.assertIn("Class cannot start in the past.", resp.context['errors'])

    def test_DuplicateCourse(self):
        resp = self.client.post("/create-course/", {
            "title": "testtitle", 
            "description": "testdescription", 
            "schedule": "testschedule"
        }, follow=True)

        self.assertEqual(resp.status_code, 400)
        self.assertIn("Course already exists", resp.context['errors'])