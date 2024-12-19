import random
from TA_Scheduler.models import User, Class, Section, userPublicInfo, userPrivateInfo
from django.shortcuts import render, redirect

##Authentication:

def pageAuthenticate(user, pageType):
    if not user or not user.userType:
        return False
    if pageType != "Admin" and pageType != "Instructor" and pageType != "TA":
        return False
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

def loginAuthenticate(email, password):
    noUser = False
    badPassword = False
    blankEntry = False
    if email == "" or password == "":
        return 0
    try:
        print(email)
        user = User.objects.get(email=email.lower())
        badPassword = (user.password != password)
    except:
        noUser = True

    if noUser:
        return 1
    elif badPassword:
        return 2
    else:
        return 3


def retrieveSessionID(request):
    try:
        userEmail = request.session["email"]
        m = User.objects.get(email=userEmail)
        return m
    except (KeyError, User.DoesNotExist):
        return None

##


##Users
def getUser(email):
    try:
        user = User.objects.get(email=email.lower())
    except User.DoesNotExist:
        return None
    return user
    #Add User
def addUser(first_name, last_name, midI, userType, email, password):
    if email == "" or password == "" or userType == "":
        return False
    return User.objects.create(fName=first_name, lName=last_name, MidInit=midI, email=email, password=password, userType=userType)
def UserAlreadyExists(request, email):
    noUser = True
    try:
        user = User.objects.get(email=email.lower())
    except User.DoesNotExist:
        noUser = False

    print(email)
    print(noUser)
    return noUser

    #Edit User
def retrieveEditUserID(request):
    try:
        editUserID = request.session["editUserID"]
        editUser = User.objects.get(id=editUserID)
    except:
        editUser = User.objects.get(email=request.session['email'])
    return editUser

def editUser(user, first_name, last_name, email, password):
    j = User.objects.get(email=user.email)
    if j.password == password:
        return False
    if "@uwm.edu" not in email:
        return False
    if not first_name or not last_name or not password:
        return False

    j.fName = first_name
    j.lName = last_name
    j.email = email
    j.password = password
    j.save()

def deleteUser(request, email, Users):
    try:
        user = User.objects.get(email)
        user.delete()
        return render(request, "manageUsers.html", {"message": "User deleted successfully", "users": Users})
    except User.DoesNotExist:
        return render(request, "manageUsers.html", {"message": "User does not exist", "users": Users})

##Sections
def createSection(request, section_name, schedule, course_id, max_capacity, ta_id=None):
    course = Class.objects.get(id=course_id)
    ta = None
    if ta_id:
        ta = User.objects.get(id=ta_id)
        
    Section.objects.create(
        section_name=section_name,
        classId=course,
        TA=ta,
        schedule=schedule,
        max_capacity=int(max_capacity)
    )