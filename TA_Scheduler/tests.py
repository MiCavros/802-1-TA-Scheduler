from django.test import TestCase, Client
from django.urls import reverse
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


class CreateCourse(TestCase):
    def setUp(self):
        self.client = Client()
        Class.objects.create(
            title="existingCourseTitle",
            description="Initial description",
            schedule="Initial schedule"
        )
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
            "schedule": "Start Date: 01/01/2025, End Date: 01/15/2025"
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['assignments'], "")  

        course = Class.objects.get(title="testtitle")
        self.assertIsNotNone(course)
        self.assertEqual(course.title, "testtitle")
        self.assertEqual(course.description, "testdescription")
        self.assertEqual(course.schedule, "Start Date: 01/01/2025, End Date: 01/15/2025")

    def test_CourseCreateWithAssignments(self):
        resp = self.client.post("/create-course/", { 
            "title": "testtitle",
            "description": "testdescription", 
            "schedule": "Start Date: 01/01/2025, End Date: 01/15/2025",
            "assignments": "testassignments"
        }, follow=True)
        
        self.assertEqual(resp.status_code, 200)

        course = Class.objects.get(title="testtitle")
        self.assertIsNotNone(course)
        self.assertEqual(course.title, "testtitle")
        self.assertEqual(course.description, "testdescription")
        self.assertEqual(course.schedule, "Start Date: 01/01/2025, End Date: 01/15/2025")
        self.assertEqual(course.assignments, "testassignments")

    def test_EmptyTitle(self):
        resp = self.client.post("/create-course/", {
            "title": "",
            "description": "testdescription",
            "schedule": "testschedule"
        }, follow=True)  
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Title cannot be empty", resp.context['errors'])

    def test_InvalidTitle(self):
        resp = self.client.post("/create-course/", {
            "title": "t" * 51,
            "description": "testdescription", 
            "schedule": "testschedule"
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Title exceeds maximum length", resp.context['errors'])

    def test_EmptyDescription(self):
        resp = self.client.post("/create-course/", { 
            "title": "testtitle",
            "description": "", 
            "schedule": "testschedule", 
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Description cannot be empty", resp.context['errors'])

    def test_InvalidDescription(self):
        resp = self.client.post("/create-course/", {
            "title": "testtitle", 
            "description": "d" * 1001,
            "schedule": "testschedule"
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Description exceeds maximum length", resp.context['errors'])

    def test_EmptySchedule(self):    
        resp = self.client.post("/create-course/", {
            "title": "testtitle",
            "description": "testdescription",
            "schedule": "",
            }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Schedule cannot be empty", resp.context['errors'])

    def test_InvalidScheduleStartEndDates(self):
        resp = self.client.post("/create-course/", { 
            "title": "testtitle",
            "description": "", 
            "schedule": "Start Date: 12/01/2024, End Date: 11/20/2024",
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Class cannot start after its end date.", resp.context['errors'])

    def test_InvalidScheduleStartDate(self):
        resp = self.client.post("/create-course/", { 
            "title": "testtitle",
            "description": "", 
            "schedule": "Start Date: 01/01/2024, End Date: 01/01/2025", 
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Class cannot start in the past.", resp.context['errors'])

    def test_DuplicateCourse(self):
        Class.objects.create(
            title="testtitle",
            description="testdescription",
            schedule="testschedule"
        )

        resp = self.client.post("/create-course/", {
            "title": "testtitle",
            "description": "testdescription", 
            "schedule": "testschedule"
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Course already exists", resp.context['errors'])

class createUserTest(TestCase):
    def setUp(self):
        self.client = Client()
        testUser = User(id=1, userType="TA", email="testUser@uwm.edu", password="1234")
        testAdminUser = User(id=2, userType="Admin", email="testAdminUser@uwm.edu", password="2222")
        testInstructor = User(id=3, userType="Instructor", email="testInstructor@uwm.edu", password="4343")
        testUser.save()
        testAdminUser.save()
        testInstructor.save()

    def test_taAccess(self):
        self.client.post("/", {"email": "testUser@uwm.edu", "password": "1234"}, follow=True)
        resp = self.client.get("/createuser/", follow=True)
        self.assertEqual(resp.context["userType"], "TA")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User Cannot Access This Page")

    def test_InstructorAccess(self):
        self.client.post("/", {"email": "testInstructor@uwm.edu", "password": "4343"}, follow=True)
        resp = self.client.get("/createuser/", follow=True)
        self.assertEqual(resp.context["userType"], "Instructor")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User Cannot Access This Page")

    def test_adminAccess(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.get("/createuser/", follow=True)
        self.assertEqual(resp.context["userType"], "Admin")
        self.assertEqual(resp.status_code, 200)

    def test_createUserSuccessfully(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createuser/", {"role": "TA", "email": "newTestUser@uwm.edu", "password": "4444",  "fName" : "Test", "midI" : "T", "lName" : "User"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User Created Successfully")
        newUser = User.objects.get(email="newtestuser@uwm.edu")
        self.assertEqual(newUser.userType, "TA")
        self.assertEqual(newUser.password, "4444")


    def test_invalidEmail(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createuser/", {"role": "TA", "email": "newTestUser", "password": "4444"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Must use valid UWM.edu email")

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

    def test_sameEmail(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createuser/", {"email": "testUser@uwm.edu", "password": "4321", "role": "TA"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "There is already a user with that email")


class EditContactInfoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            id=1, userType="TA", email="testUser@uwm.edu", password="1234"
        )
        self.public_info = userPublicInfo.objects.create(
            user=self.user, email="testUser@uwm.edu", phone="1234567890"
        )

    # Positive Test: Edit contact info with valid data
    def test_editContactInfoSuccess(self):
        resp = self.client.post("/edit-contact-info/", {
            "email": "newEmail@uwm.edu",
            "phone": "9876543210",
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Contact information updated successfully")

        updated_info = userPublicInfo.objects.get(user=self.user)
        self.assertEqual(updated_info.email, "newEmail@uwm.edu")
        self.assertEqual(updated_info.phone, "9876543210")

    # Negative Test: Empty email field
    def test_emptyEmail(self):
        resp = self.client.post("/edit-contact-info/", {
            "email": "",
            "phone": "9876543210",
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Email cannot be empty", resp.context['errors'])

    # Negative Test: Empty phone field
    def test_emptyPhone(self):
        resp = self.client.post("/edit-contact-info/", {
            "email": "testUser@uwm.edu",
            "phone": "",
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Phone number cannot be empty", resp.context['errors'])

    # Negative Test: Phone number less than 10 digits
    def test_invalidPhoneLength(self):
        resp = self.client.post("/edit-contact-info/", {
            "email": "testUser@uwm.edu",
            "phone": "12345",
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Phone number must be at least 10 digits", resp.context['errors'])

    # Negative Test: Invalid email domain
    def test_invalidEmail(self):
        resp = self.client.post("/edit-contact-info/", {
            "email": "invalidEmail@gmail.com",
            "phone": "9876543210",
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Email must be a valid @uwm.edu address", resp.context['errors'])

    # Negative Test: Unauthenticated access
    def test_unauthenticatedAccess(self):
        self.client.logout()
        resp = self.client.post("/edit-contact-info/", {
            "email": "newEmail@uwm.edu",
            "phone": "9876543210",
        }, follow=True)

        self.assertEqual(resp.status_code, 403)  # Forbidden
        self.assertIn("Authentication required", resp.context['errors'])

    # Negative Test: Unauthorized user trying to edit another user's contact info
    def test_unauthorizedAccess(self):
        other_user = User.objects.create(
            id=2, userType="Instructor", email="otherUser@uwm.edu", password="4321"
        )
        self.client.force_login(other_user)

        resp = self.client.post("/edit-contact-info/", {
            "email": "newEmail@uwm.edu",
            "phone": "9876543210",
        }, follow=True)

        self.assertEqual(resp.status_code, 403)  # Forbidden
        self.assertIn("Permission denied", resp.context['errors'])

class createSectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        testAdminUser = User(id=2, userType="ADMIN", email="testAdminUser@uwm.edu", password="2222")
        testAdminUser.save()
        testInstructor = User(id=3, userType="INSTRUCTOR", email="testInstructor@uwm.edu", password = "4444")
        testInstructor.save()

        testCourse = Class(id=2, title="testCourse", instructor=testInstructor, schedule="Start Date: 01/01/2025, End Date: 01/15/2025")
        testCourse.save()

    def test_successfulSectionCreation(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createsection/",{"section_name": "testSection", "instructor_id" : 3, "schedule": "Tuesday, 2:00 PM - 4:00 PM", "course_id": 2, "max_capacity" : 10}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Section Created Successfully")
        newSection = Section.objects.get(classId=2)

    def test_noInstructor(self ):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createsection/", {"section_name": "testSection", "schedule": "Tuesday, 2:00 PM - 4:00 PM", "course_id" : 2, "max_capacity" : 10},follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Instructor Field is Required")
    def test_noName(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createsection/",{"instructor_id": 3, "schedule": "Tuesday, 2:00 PM - 4:00 PM", "course_id": 2, "max_capacity" : 10}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Name Field is Required")
    def test_invalidName(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createsection/",{"section_name": "##$$*)(*", "instructor_id" : 3, "schedule": "Tuesday, 2:00 PM - 4:00 PM", "course_id": 2, "max_capacity" : 10}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Section Name is Invalid")
    def test_noCourse(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/createsection/", {"section_name": "testSection", "instructor_id" : 3, "schedule": "Tuesday, 2:00 PM - 4:00 PM", "max_capacity" : 10},follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Course Field is Required")
    def test_noCapacity(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        response = self.client.post('/createsection/', {
            'section_name': 'testSection',
            'instructor_id': '3',
            'schedule': 'Tuesday, 2:00 PM - 4:00 PM',
            'course_id': '2',
        }, follow=True)
        self.assertEqual(response.context["message"], "Capacity Field is Required")


class DeleteUserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create(id=1, userType="Admin", email="admin@uwm.edu", password="adminpass")
        self.user_to_delete = User.objects.create(id=2, userType="TA", email="deleteMe@uwm.edu", password="deletepass")
        self.client.post("/", {"email": "admin@uwm.edu", "password": "adminpass"}, follow=True)

    def test_deleteUser(self):
        resp = self.client.post(reverse('delete_user'), {"user_id": self.user_to_delete.id}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User deleted successfully")
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.user_to_delete.id)

    def test_deleteNonExistentUser(self):
        resp = self.client.post(reverse('delete_user'), {"user_id": 999}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User does not exist")

class testManageUsers(TestCase):
    def setUp(self):
        self.client = Client()
        testAdminUser = User(id=2, userType="ADMIN", email="testAdminUser@uwm.edu", password="2222")
        testAdminUser.save()
        testInstructor = User(id=3, userType="INSTRUCTOR", email="testInstructor@uwm.edu", password="4444")
        testInstructor.save()
        testUser = User(id=1, userType="TA", email="testUser@uwm.edu", password="1234")
        testUser.save()

    def test_taAccess(self):
        self.client.post("/", {"email": "testUser@uwm.edu", "password": "1234"}, follow=True)
        resp = self.client.get("/manageusers/", follow=True)
        self.assertEqual(resp.context["userType"], "TA")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User Cannot Access This Page")

    def test_InstructorAccess(self):
        self.client.post("/", {"email": "testInstructor@uwm.edu", "password": "4444"}, follow=True)
        resp = self.client.get("/manageusers/", follow=True)
        self.assertEqual(resp.context["userType"], "Instructor")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User Cannot Access This Page")

    def test_adminAccess(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.get("/manageusers/", follow=True)
        self.assertEqual(resp.context["userType"], "Admin")
        self.assertEqual(resp.status_code, 200)

    ##Tests for successfull display of all users, tests for attempting to delete admins, and tests for successful redirect

class testEditAccount(TestCase):
    def setUp(self):
        testAdminUser = User(id=2, userType="ADMIN", email="testAdminUser@uwm.edu", password="2222")
        testAdminUser.save()
        testInstructor = User(id=3, userType="INSTRUCTOR", email="testInstructor@uwm.edu", password="4444")
        testInstructor.save()
        testUser = User(id=1, userType="TA", email="testUser@uwm.edu", password="1234")
        testUser.save()

    def test_taAccess(self):
        self.client.post("/", {"email": "testUser@uwm.edu", "password": "1234"}, follow=True)
        resp = self.client.get("/editAccount/", follow=True)
        self.assertEqual(resp.context["userType"], "TA")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User Cannot Access This Page")

    def test_InstructorAccess(self):
        self.client.post("/", {"email": "testInstructor@uwm.edu", "password": "4444"}, follow=True)
        resp = self.client.get("/editAccount/", follow=True)
        self.assertEqual(resp.context["userType"], "Instructor")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "User Cannot Access This Page")

    def test_adminAccess(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.get("/editAccount/", follow=True)
        self.assertEqual(resp.context["userType"], "Admin")
        self.assertEqual(resp.status_code, 200)

    def test_editUserSuccessfully(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/editaccount/1", {"first_name": "NewTestUser", "email": "newNewTestUser@uwm.edu", "last_name": "NewLastName",  "password" : "1222", "confirm_password" : "1222", "phone" : "4144444444"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Accounted Updated Successfully")
        newUser = User.objects.get(email="newnewtestuser@uwm.edu")
        self.assertEqual(newUser.userType, "TA")
        self.assertEqual(newUser.password, "1222")
        self.assertEqual(newUser.first_name, "NewTestUser")
        self.assertEqual(newUser.last_name, "NewLastName")
        self.assertEqual(newUser.phone, "4144444444")

    def test_invalidEmail(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/editaccount/1", {"first_name": "NewTestUser", "email": "newNewTestUser", "last_name": "NewLastName",  "password" : "1222", "confirm_password" : "1222", "phone" : "4144444444"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Must use valid UWM.edu email")

    def test_NoEmail(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/editaccount/1",{"first_name": "NewTestUser", "last_name": "NewLastName", "password": "1222", "confirm_password": "1222", "phone": "4144444444"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Email is a required field")

    def test_PasswordsDontMatch(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/editaccount/1",{"first_name": "NewTestUser", "last_name": "NewLastName", "password": "1222","confirm_password": "1232", "phone": "4144444444"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Passwords Don't Match")

    def test_InvalidPhone(self):
        self.client.post("/", {"email": "testAdminUser@uwm.edu", "password": "2222"}, follow=True)
        resp = self.client.post("/editaccount/1",{"first_name": "NewTestUser", "last_name": "NewLastName", "password": "1222","confirm_password": "1222", "phone": "4"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "Invalid Phone Number")

class AssignSectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create(id=1, userType="Admin", email="adminUser@uwm.edu", password="1234")
        self.instructor_user = User.objects.create(id=2, userType="Instructor", email="instructorUser@uwm.edu", password="5678")
        self.ta_user = User.objects.create(id=3, userType="TA", email="taUser@uwm.edu", password="4321")

        # Create Class and Section
        self.course = Class.objects.create(id=1, title="Test Course", description="Test Description", schedule="Start Date: 01/01/2025, End Date: 05/01/2025")
        self.section = Section.objects.create(id=1, section_number="101", course=self.course)

    # Positive Test: Admin assigns a TA to a section successfully
    def test_adminAssignTASuccess(self):
        self.client.force_login(self.admin_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": self.ta_user.id,
            "section_id": self.section.id,
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "TA successfully assigned to the section.")
        updated_section = Section.objects.get(id=self.section.id)
        self.assertEqual(updated_section.ta, self.ta_user)

    # Positive Test: Instructor assigns a TA to a section successfully
    def test_instructorAssignTASuccess(self):
        self.client.force_login(self.instructor_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": self.ta_user.id,
            "section_id": self.section.id,
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["message"], "TA successfully assigned to the section.")
        updated_section = Section.objects.get(id=self.section.id)
        self.assertEqual(updated_section.ta, self.ta_user)

    # Negative Test: TA tries to assign themselves to a section
    def test_taAssignThemselves(self):
        self.client.force_login(self.ta_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": self.ta_user.id,
            "section_id": self.section.id,
        }, follow=True)

        self.assertEqual(resp.status_code, 403)  # Forbidden
        self.assertIn("TAs cannot assign themselves to sections", resp.context['errors'])

    # Negative Test: TA tries to assign another TA to a section
    def test_taAssignOtherTA(self):
        other_ta = User.objects.create(
            id=4, userType="TA", email="otherTA@uwm.edu", password="9876"
        )
        self.client.force_login(self.ta_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": other_ta.id,
            "section_id": self.section.id,
        }, follow=True)

        self.assertEqual(resp.status_code, 403)  # Forbidden
        self.assertIn("TAs cannot assign other TAs to sections", resp.context['errors'])

    # Negative Test: Empty TA 
    def test_emptyTA(self):
        self.client.force_login(self.admin_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": "",
            "section_id": self.section.id,
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("TA ID cannot be empty", resp.context['errors'])

    # Negative Test: Empty Section 
    def test_emptySection(self):
        self.client.force_login(self.admin_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": self.ta_user.id,
            "section_id": "",
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Section ID cannot be empty", resp.context['errors'])

    # Negative Test: Invalid TA 
    def test_invalidTA(self):
        self.client.force_login(self.admin_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": 999,  # Non-existent TA ID
            "section_id": self.section.id,
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("TA not found", resp.context['errors'])

    # Negative Test: Invalid Section
    def test_invalidSection(self):
        self.client.force_login(self.admin_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": self.ta_user.id,
            "section_id": 999,  # Non-existent Section ID
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Section not found", resp.context['errors'])

    # Negative Test: TA already assigned to the section
    def test_taAlreadyAssigned(self):
        self.section.ta = self.ta_user
        self.section.save()
        self.client.force_login(self.admin_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": self.ta_user.id,
            "section_id": self.section.id,
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("TA is already assigned to this section", resp.context['errors'])

    # Negative Test: Section already assigned to another TA
    def test_sectionAssignedToAnotherTA(self):
        other_ta = User.objects.create(
            id=4, userType="TA", email="otherTA@uwm.edu", password="9876"
        )
        self.section.ta = other_ta
        self.section.save()
        self.client.force_login(self.admin_user)
        resp = self.client.post("/assign-section/", {
            "ta_id": self.ta_user.id,
            "section_id": self.section.id,
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("This section is already assigned to another TA", resp.context['errors'])



