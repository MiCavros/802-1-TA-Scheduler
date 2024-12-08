import random
from TA_Scheduler.models import User, Class, Section, userPublicInfo, userPrivateInfo
from django.shortcuts import render, redirect

##Authentication:

def pageAuthenticate(user, pageType):
    if pageType == "Admin":
        if user.userType == "Admin":
            return True
        else:
            return False
    if pageType == "Instructor":
        if user.userType == "TA":
            return False
        else:
            return True
    if pageType == "TA":
        return True

def loginAuthenticate(request, email, password):
    noUser = False
    badPassword = False
    blankEntry = False
    if email == "" or password == "":
        return render(request, "login.html", {"message": "Email and/or Password cannot be blank"})
    try:
        user = User.objects.get(email=request.POST['email'].lower())
        badPassword = (user.password != request.POST['password'])
    except:
        noUser = True

    if noUser:
        return render(request, "login.html", {"message": "No User with this Email"})
    elif badPassword:
        return render(request, "login.html", {"message": "Incorrect Password"})
    else:
        request.session["email"] = user.email
        return redirect("/home/")


def retrieveSessionID(request):
    userEmail = request.session["email"]
    m = User.objects.get(email=userEmail)
    return m

##


##Users
    #Add User
def addUser(first_name, last_name, midI, userType, email, password):
    n = User.objects.create(fName= first_name, lName = last_name, MidInit = midI, email = email, password = password, userType = userType)

    #Edit User
def retrieveEditUserID(request):

    try:
        editUserID = request.session["editUserEmail"]
        editUser = User.objects.get(email=editUserID)
    except:
        editUser = User.objects.get(email=request.session['email'])
    return editUser

def editUser(user, first_name, last_name, email, password):
    j = User.objects.get(email=user.email)
    j.fName = first_name
    j.lName = last_name
    j.email = email
    j.password = password
    j.save()

def deleteUser(request, d, Users):
    try:
        user = User.objects.get(id=d)
        user.delete()
        return render(request, "manageUsers.html", {"message": "User deleted successfully", "users": Users})
    except User.DoesNotExist:
        return render(request, "manageUsers.html", {"message": "User does not exist", "users": Users})

##Sections
def createSection(request, section_name, instructor_id, schedule, course_id, max_capacity):
    instructor = User.objects.get(id=instructor_id)
    course = Class.objects.get(id=course_id)
    Section.objects.create(
        sectionId=Section.objects.count() + 1,
        section_name=section_name,
        classId=course,
        TA=instructor,
        schedule=schedule,
        max_capacity=int(max_capacity)
    )