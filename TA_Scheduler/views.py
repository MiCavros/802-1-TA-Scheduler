import random
from idlelib.pyshell import UserInputTaggingDelegator
from operator import truediv
from sched import scheduler

from django.db.models.fields import return_None
from django.db.utils import IntegrityError
from datetime import datetime
from django.shortcuts import render, redirect
from django.template.defaultfilters import length
from django.views import View
from .models import User, userPublicInfo, userPrivateInfo, Class, Section

class Login(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        noUser = False
        badPassword = False
        blankEntry = False
        if request.POST['email'] == "" or request.POST['password'] == "":
            return render(request, "login.html", {"message": "Email and/or Password cannot be blank"})
        try:
            user = User.objects.get(email=request.POST['email'].lower())
            badPassword = (user.password != request.POST['password'])
        except:
            noUser = True

        if noUser:
            return render(request, "login.html", {"message": "No User with this Email"})
        elif badPassword:
            return render(request,"login.html",{"message":"Incorrect Password"})
        else:
            request.session["id"] = user.id
            return redirect("/home/")

class Home(View):
    def get(self, request):
        userID = request.session["id"]
        m = User.objects.get(id=userID)
        if m.userType == "Admin":
            return render(request, 'adminHome.html', {"userType": m.userType, "name":  m.fName})
        else:
            return render(request, 'home.html', {"userType": m.userType, "name":  m.fName})

class CreateUser(View):
    def get(self, request):
        userID = request.session["id"]
        m = User.objects.get(id=userID)
        if m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page", "userType": m.userType})
        else:
            return render(request, 'createUser.html', {"message": "", "userType": m.userType})
    def post(self, request):
        #Code the post please
        userID = request.session["id"]
        m = User.objects.get(id=userID)
        noUser = False

        if request.POST['email'] == "":
            return render(request, "createUser.html", {"message": "Email is a required field", "userType": m.userType})
        if request.POST['password'] == "":
            return render(request, "createUser.html",
                          {"message": "Password is a required field", "userType": m.userType})
        if request.POST['role'] == "":
            return render(request, "createUser.html",
                          {"message": "Role is a required field", "userType": m.userType})
        if "@uwm.edu" not in request.POST['email']:
            return render(request, "createUser.html", {"message": "Must use valid UWM.edu email"})
        try:
            user = User.objects.get(request.POST['email'].lower())
        except:
            noUser = True
        if not noUser:
            return render(request, "createUser.html", {"message": "There is already a user with that email"})
        newID = generateUserID(request.POST['email'].lower)

        addUser(newID, request.POST['fName'].lower(), request.POST['lName'].lower(),request.POST['midI'].lower, request.POST['role'], request.POST['email'].lower(), request.POST['password'])
        #newUser = User.objects.create(fName=request.POST['fName'].lower(), lName=request.POST['lName'].lower(), MidInit=request.POST['midI'].lower(), id=newID, userType=request.POST['role'], email=request.POST['email'].lower(), password=request.POST['password'].lower())
        return render(request, 'createUser.html', {"message" : "User Created Successfully", "userType": m.userType})

class CreateCourse(View):
    def get(self, request):
        return render(request, 'createCourse.html')

    def post(self, request):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        schedule = request.POST.get('schedule', '').strip()
        assignments = request.POST.get('assignments', '').strip()

        errors = []

        # Validation for title
        if not title:
            errors.append("Title cannot be empty")
        elif len(title) > 50:
            errors.append("Title exceeds maximum length")

        # Validation for description
        if not description:
            errors.append("Description cannot be empty")
        elif len(description) > 1000:
            errors.append("Description exceeds maximum length")

        # Validation for schedule
        if not schedule:
            errors.append("Schedule cannot be empty")
        else:
            # Validate schedule format
            try:
                start_date_str = schedule.split("Start Date: ")[1].split(",")[0].strip()
                end_date_str = schedule.split("End Date: ")[1].strip()

                start_date = datetime.strptime(start_date_str, "%m/%d/%Y")
                end_date = datetime.strptime(end_date_str, "%m/%d/%Y")

                # Check if start date is after end date
                if start_date > end_date:
                    errors.append("Class cannot start after its end date.")
                # Check if start date is in the past
                if start_date < datetime.now():
                    errors.append("Class cannot start in the past.")
            except (IndexError, ValueError):
                errors.append("Schedule format is incorrect. Use 'Start Date: MM/DD/YYYY, End Date: MM/DD/YYYY'.")

        # Check for duplicate course
        if Class.objects.filter(title=title).exists():
            errors.append("Course already exists")

        # If there are errors, return to the same page with errors
        if errors:
            return render(request, 'createCourse.html', {
                'errors': errors,
                'title': title,
                'description': description,
                'schedule': schedule,
                'assignments': assignments
            })

        # If no errors, create the course
        new_course = Class.objects.create(
            title=title,
            description=description,
            schedule=schedule,
            assignments=assignments
        )

        return render(request, 'createCourse.html', {
            'message': "Course created successfully!",
            'title': new_course.title,
            'description': new_course.description,
            'schedule': new_course.schedule,
            'assignments': new_course.assignments
        })

class CreateSection(View):
    def get(self, request):
        return render(request, 'createSection.html')
    def post(self, request):
        section_name = request.POST.get("section_name")
        instructor_id = request.POST.get("instructor_id")
        schedule = request.POST.get("schedule")
        course_id = request.POST.get("course_id")
        max_capacity = request.POST.get("max_capacity")

        if not section_name:
            return render(request, "createSection.html", {"message": "Name Field is Required"})
        if not instructor_id:
            return render(request, "createSection.html", {"message": "Instructor Field is Required"})
        if not course_id:
            return render(request, "createSection.html", {"message": "Course Field is Required"})
        if not max_capacity or not max_capacity.isdigit():
            return render(request, "createSection.html", {"message": "Capacity Field is Required"})
        if not section_name.isalnum():
            return render(request, "createSection.html", {"message": "Section Name is Invalid"})

        createSection(request, section_name, instructor_id, schedule, course_id, max_capacity)


        return render(request, "createSection.html", {"message": "Section Created Successfully"})

class AssignSection(View):
    def get(self, request):
        return render(request, 'assignSections.html', )
    def post(self, request):
        return render(request, "assignSections.html")

class editContactInfo(View):
    def get(self, request):
        return render(request, 'editContactInfo.html')
    def post(self, request):
        return render(request, 'editContactInfo.html')


class manageUsers(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m.userType == "Admin":
            Users = User.objects.all()

            return render(request, 'manageUsers.html', {"userType": m.userType, "users": Users})
        else:
            return render(request, 'userNoAccess.html', {"userType": m.userType, "message": "User Cannot Access This Page"})

    def post(self, request):
        editUser_id = request.POST.get("user")
        request.session["editUserID"] = editUser_id
        Users = User.objects.all()

        if request.POST["action"] == "edit":
            return redirect("/editaccount/")
        else:
            print(editUser_id)
            try:
                user = User.objects.get(id=editUser_id)
                user.delete()
                return render(request, "manageUsers.html", {"message": "User deleted successfully", "users": Users})
            except User.DoesNotExist:
                return render(request, "manageUsers.html", {"message": "User does not exist", "users": Users})


class editAccount(View):

    def get(self, request):
        editUser = retrieveEditUserID(request)
        m = retrieveSessionID(request)


        return render(request, 'editAccount.html', {"userType": m.userType, "user": editUser})

    def post(self, request):
        User = retrieveEditUserID(request)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not email:
            return render(request, 'editAccount.html', {"message": "Email is a required field"})
        if "@uwm.edu" not in email:
            return render(request, 'editAccount.html', {"message": "Must use valid UWM.edu email"})
        if password:
            if password != confirm_password:
                return render(request, 'editAccount.html', {"message": "Passwords Don't match"})


        editUser(User, first_name, last_name, email, password)


        return render(request, 'editAccount.html', {"message": "Account Edited Successfully", "user" : editUser})
    
class assignSections(View):
    def get(self, request):
        return render(request, 'assignSections.html')
    def post(self, request):
        return render(request, 'assignSections.html')
    
class adminEditContactInfo(View):
    def get(self, request):
        return render(request, 'adminEditContactInfo.html')
    def post(self, request):
        return render(request, 'adminEditContactInfo.html')

def deleteUser(request, d, Users):
    try:
        user = User.objects.get(id=d)
        user.delete()
        return render(request, "manageUsers.html", {"message": "User deleted successfully", "users": Users})
    except User.DoesNotExist:
        return render(request, "manageUsers.html", {"message": "User does not exist", "users": Users})

def retrieveSessionID(request):
    userID = request.session["id"]
    m = User.objects.get(id=userID)
    return m

def retrieveEditUserID(request):

    try:
        editUserID = request.session["editUserID"]
        editUser = User.objects.get(id=editUserID)
    except:
        editUser = User.objects.get(id=request.session['id'])
    return editUser

def editUser(user, first_name, last_name, email, password):
    j = User.objects.get(id=user.id)
    j.fName = first_name
    j.lName = last_name
    j.email = email
    j.password = password
    j.save()

def addUser(id, first_name, last_name, midI, userType, email, password):
    n = User.objects.create(id= id,fName= first_name, lName = last_name, MidInit = midI, email = email, password = password, userType = userType)

def createSection(request, section_name, instructor_id, schedule, course_id, max_capacity):
    instructor = User.objects.get(id=instructor_id)
    course = Class.objects.get(id=course_id)
    Section.objects.create(
        sectionId=Section.objects.count() + 1,
        classId=course,
        TA=instructor,
        schedule=schedule,
        max_capacity=int(max_capacity)
    )
def generateUserID(email):
    idInUse = True

    while idInUse:
        newID = random.randint(0, 500)
        try:
            userID = User.objects.get(id=newID)
            idInUse = True
        except:
            idInUse = False
    return newID