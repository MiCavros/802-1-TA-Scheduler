from django.db.models.fields import return_None
from django.shortcuts import render, redirect
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
            user = User.objects.get(email=request.POST['email'])
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
        return render(request, 'home.html', {"userType": m.userType, "name":  m.fName})
    
class CreateUser(View):
    def get(self, request):
        userID = request.session["id"]
        m = User.objects.get(id=userID)
        return render(request, 'createUser.html', {"message": "", "userType": m.userType})
    def post(self, request):
        #Code the post please
        userID = request.session["id"]
        m = User.objects.get(id=userID)
        return render(request, 'createUser.html', {"message" : "", "userType": m.userType})
    pass

class CreateCourse(View):
    def get(self, request):
        return render(request, 'createCourse.html')
    def post(self, request):
        # if request.POST['title'] == "":
        #     return render(request, "createCourse.html", {"message": "Course title cannot be blank."})

        if request.POST['description'] == "":
            return render(request, "createCourse.html", {"message": "Course description cannot be blank."})

        if request.POST['schedule'] == "":
            return render(request, "createCourse.html", {"message": "Course schedule cannot be blank."})

        # userID = request.session["id"]
        # m = User.objects.get(id=userID)
        # invalidUserType = (userType != "Instructor" or userType != "Admin")

        # if invalidUserType:
        #     return render(request, "createCourse.html", {"message": "You are not able to access this page."})

        return render(request, 'createCourse.html', {"title": request.POST['title'], "description":  request.POST['description'], "schedule": request.POST['schedule']})
class CreateSection(View):
    def get(self, request):
        return render(request, 'createSection.html')
    def post(self, request):
        return render(request, "createSection.html")

class AssignSection(View):
    def get(self, request):
        return render(request, 'assignSections.html')
    def post(self, request):
        return render(request, "assignSections.html")

class editContactInfo(View):
    def get(self, request):
        return render(request, 'editContactInfo.html')
    def post(self, request):
        return render(request, 'editContactInfo.html')

class editUser(View):
    def get(self, request):
        return render(request, 'editUser.html')
    def post(self, request):
        return render(request, 'editUser.html')

class manageUser(View):
    def get(self, request):
        return render(request, 'manageUsers.html')
    def post(self, request):
        return render(request, 'manageUsers.html')
