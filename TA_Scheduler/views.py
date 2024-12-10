import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q

from .main import retrieveSessionID, pageAuthenticate, loginAuthenticate, retrieveEditUserID, editUser, createSection, \
    addUser
from .models import User, Class, Section

class Login(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        password = request.POST['password']
        email = request.POST['email']
        return loginAuthenticate(request, email, password)


class Home(View):
    def get(self, request):
        m = retrieveSessionID(request)
        return render(request, 'home.html', {"user": m})

class CreateUser(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if pageAuthenticate(m, "Admin"):
            return render(request, 'userNoAccess.html',
                          {"message": "User Cannot Access This Page", "userType": m.userType})
        else:
            return render(request, 'createUser.html', {"message": "", "userType": m.userType})

    def post(self, request):
        m = retrieveSessionID(request)
        if m.userType == "Admin":
            userID = request.session["email"]
            m = User.objects.get(email=userID)
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


            addUser(request.POST['fName'].lower(), request.POST['lName'].lower(),request.POST['midI'].lower, request.POST['role'], request.POST['email'].lower(), request.POST['password'])
            #newUser = User.objects.create(fName=request.POST['fName'].lower(), lName=request.POST['lName'].lower(), MidInit=request.POST['midI'].lower(), id=newID, userType=request.POST['role'], email=request.POST['email'].lower(), password=request.POST['password'].lower())
            return render(request, 'createUser.html', {"message" : "User Created Successfully", "userType": m.userType})
        else:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})

class CreateCourse(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m.userType in ["Admin", "Instructor"]:
            instructors = User.objects.filter(userType='Instructor')
            return render(request, 'createCourse.html', {'instructors': instructors})
        else:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})

    def post(self, request):
        m = retrieveSessionID(request)
        if m.userType in ["Admin", "Instructor"]:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            days = request.POST.getlist('days[]')
            assignments = request.POST.get('assignments', '').strip()
            instructor_id = request.POST.get('instructor_id')
            location = request.POST.get('location', '').strip()

            errors = []
            instructors = User.objects.filter(userType='Instructor')

            if not title or not description or not instructor_id:
                errors.append("Title, description and instructor are required")

            if not all([start_date, end_date, start_time, end_time, days]):
                errors.append("All schedule fields are required")
            else:
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                    today = datetime.now().date()

                    if start_date_obj > end_date_obj:
                        errors.append("Class cannot start after its end date")
                    if start_date_obj < today:
                        errors.append("Class cannot start in the past")

                    schedule = f"Days: {', '.join(days)}; Time: {start_time}-{end_time}; Start Date: {start_date}; End Date: {end_date}"
                except ValueError:
                    errors.append("Invalid date format")

            if Class.objects.filter(title=title).exists():
                errors.append("Course already exists")

            if errors:
                context = {
                    'errors': errors,
                    'title': title,
                    'description': description,
                    'assignments': assignments,
                    'instructors': instructors,
                    'start_date': start_date,
                    'end_date': end_date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'days': days,
                    'location': location
                }
                return render(request, 'createCourse.html', context)

            new_course = Class.objects.create(
                title=title,
                description=description,
                schedule=schedule,
                assignments=assignments,
                location=location
            )

            return render(request, 'createCourse.html', {
                'message': "Course created successfully!",
                'instructors': instructors
            })

        return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})

class CreateSection(View):
    def get(self, request):
        courses = Class.objects.all()
        instructors = User.objects.filter(userType='Instructor')
        return render(request, 'createSection.html', {
            'courses': courses,
            'instructors': instructors
        })

    def post(self, request):
        section_name = request.POST.get("section_name")
        instructor_id = request.POST.get("instructor_id")
        course_id = request.POST.get("course_id")
        max_capacity = request.POST.get("max_capacity")
        
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        days = request.POST.getlist('days[]')

        errors = []
        context = {
            'courses': Class.objects.all(),
            'instructors': User.objects.filter(userType='Instructor')
        }

        if not all([section_name, instructor_id, course_id, max_capacity]):
            errors.append("All fields are required")
        if not section_name.isalnum():
            errors.append("Section Name is Invalid")
        if max_capacity and not max_capacity.isdigit():
            errors.append("Capacity must be a number")

        if not all([start_date, end_date, start_time, end_time, days]):
            errors.append("All schedule fields are required")
        else:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                today = datetime.now().date()

                if start_date_obj > end_date_obj:
                    errors.append("Section cannot start after its end date")
                if start_date_obj < today:
                    errors.append("Section cannot start in the past")

                schedule = f"Days: {', '.join(days)}; Time: {start_time}-{end_time}; Start Date: {start_date}; End Date: {end_date}"
            except ValueError:
                errors.append("Invalid date format")

        if errors:
            context['message'] = "\n".join(errors)
            return render(request, "createSection.html", context)

        createSection(request, section_name, instructor_id, schedule, course_id, max_capacity)
        context['message'] = "Section Created Successfully"
        return render(request, "createSection.html", context)

class AssignSection(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m.userType in ["Admin", "Instructor"]:
            context = {
                'courses': Class.objects.all(),
                'instructors': User.objects.filter(userType='Instructor'),
                'tas': User.objects.filter(userType='TA'),
                'sections': Section.objects.all(),
                'message': request.GET.get('message', '')
            }
            return render(request, 'assignSections.html', context)
        return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})

    def post(self, request):
        m = retrieveSessionID(request)
        if m.userType in ["Admin", "Instructor"]:
            ta_id = request.POST.get("ta_id")
            section_id = request.POST.get("section_id")
            try:
                section = Section.objects.get(sectionId=section_id)
                ta = User.objects.get(id=ta_id)
                section.TA = ta
                section.save()
                context = {
                    'courses': Class.objects.all(),
                    'instructors': User.objects.filter(userType='Instructor'),
                    'tas': User.objects.filter(userType='TA'),
                    'sections': Section.objects.all(),
                    'message': "TA successfully assigned to the section."
                }
            except Section.DoesNotExist:
                context = {
                    'courses': Class.objects.all(),
                    'instructors': User.objects.filter(userType='Instructor'),
                    'tas': User.objects.filter(userType='TA'),
                    'sections': Section.objects.all(),
                    'message': "Section does not exist."
                }
            except User.DoesNotExist:
                context = {
                    'courses': Class.objects.all(),
                    'instructors': User.objects.filter(userType='Instructor'),
                    'tas': User.objects.filter(userType='TA'),
                    'sections': Section.objects.all(),
                    'message': "TA does not exist."
                }
            return render(request, 'assignSections.html', context)
        return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})

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
        m = retrieveSessionID(request)
        if m.userType == "Admin":
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
        else:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})

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
    
    
class UpdatePassword(View):
    def post(self, request):
        user = retrieveSessionID(request)
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        if user.password != current_password:
            return render(request, 'editAccount.html', {"message": "Current password is incorrect", "user": user})
        if new_password != confirm_new_password:
            return render(request, 'editAccount.html', {"message": "New passwords do not match", "user": user})

        user.password = new_password
        user.save()
        return render(request, 'editAccount.html', {"message": "Password updated successfully", "user": user})

class TaViewAssignmentsPage(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m.userType == "TA":
            assignments = Section.objects.filter(TA=m)
            return render(request, 'viewAssignments.html', {"assignments": assignments})
        else:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})

class ReadPublicContactInfoPage(View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        if search_query:
            users = User.objects.filter(
                Q(fName__icontains=search_query) | Q(lName__icontains=search_query) | Q(email__icontains=search_query)
            )
        else:
            users = User.objects.all()
        return render(request, 'readPublicContactInfo.html', {'users': users})
