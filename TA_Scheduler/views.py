import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q, Prefetch
from django.template.defaultfilters import register

from .main import retrieveSessionID, pageAuthenticate, loginAuthenticate, retrieveEditUserID, editUser, createSection, \
    addUser
from .models import User, Class, Section, Message

@register.filter(name='split')
def split(value, arg):
    return [part.strip() for part in value.split(arg)]

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
        if m is None:
            return redirect('/')
        return render(request, 'home.html', {"user": m})

class CreateUser(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None or pageAuthenticate(m, "Admin"):
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page", "userType": m.userType if m else "Guest"})
        return render(request, 'createUser.html', {"message": "", "userType": m.userType})

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        userID = request.session["email"]
        m = User.objects.get(email=userID)
        noUser = False

        if request.POST['email'] == "":
            return render(request, "createUser.html", {"message": "Email is a required field", "userType": m.userType})
        if request.POST['password'] == "":
            return render(request, "createUser.html", {"message": "Password is a required field", "userType": m.userType})
        if request.POST['role'] == "":
            return render(request, "createUser.html", {"message": "Role is a required field", "userType": m.userType})
        if "@uwm.edu" not in request.POST['email']:
            return render(request, "createUser.html", {"message": "Must use valid UWM.edu email"})
        try:
            user = User.objects.get(email=request.POST['email'].lower())
        except User.DoesNotExist:
            noUser = True
        if not noUser:
            return render(request, "createUser.html", {"message": "There is already a user with that email"})

        addUser(request.POST['fName'].lower(), request.POST['lName'].lower(), request.POST['midI'].lower(), request.POST['role'], request.POST['email'].lower(), request.POST['password'])
        return render(request, 'createUser.html', {"message": "User Created Successfully", "userType": m.userType})

class CreateCourse(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType not in ["Admin", "Instructor"]:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        instructors = User.objects.filter(userType='Instructor')
        return render(request, 'createCourse.html', {'instructors': instructors})

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType not in ["Admin", "Instructor"]:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
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

class CreateSection(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None:
            return redirect('/login/')
        courses = Class.objects.all()
        instructors = User.objects.filter(userType='Instructor')
        return render(request, 'createSection.html', {
            'courses': courses,
            'instructors': instructors
        })

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None:
            return redirect('/login/')
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
        if not all(char.isalnum() or char.isspace() for char in section_name):
            errors.append("Section Name can only contain letters, numbers, and spaces")
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
        if m is None or m.userType not in ["Admin", "Instructor"]:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        context = {
            'courses': Class.objects.all(),
            'instructors': User.objects.filter(userType='Instructor'),
            'tas': User.objects.filter(userType='TA'),
            'sections': Section.objects.all(),
            'message': request.GET.get('message', '')
        }
        return render(request, 'assignSections.html', context)

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType not in ["Admin", "Instructor"]:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
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

class editContactInfo(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None:
            return redirect('/login/')
        return render(request, 'editContactInfo.html', {"user": m})

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None:
            return redirect('/login/')
        
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        m.phone = phone
        m.address = address
        m.save()

        return render(request, 'editContactInfo.html', {"user": m, "message": "Contact information updated successfully"})

class manageUsers(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        Users = User.objects.all()
        return render(request, 'manageUsers.html', {"userType": m.userType, "users": Users})

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
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
        if m is None:
            return redirect('/login/')
        return render(request, 'editAccount.html', {"userType": m.userType, "user": editUser})

    def post(self, request):
        editUser = retrieveEditUserID(request)
        m = retrieveSessionID(request)
        if m is None:
            return redirect('/login/')
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        context = {
            "user": editUser,
            "first_name": first_name or editUser.fName,
            "last_name": last_name or editUser.lName,
            "email": email or editUser.email
        }

        if not email:
            context["message"] = "Email is a required field"
            return render(request, 'editAccount.html', context)
        if "@uwm.edu" not in email:
            context["message"] = "Must use valid UWM.edu email"
            return render(request, 'editAccount.html', context)
        if password:
            if password != confirm_password:
                context["message"] = "Passwords don't match"
                return render(request, 'editAccount.html', context)
            editUser.password = password

        editUser.fName = first_name or editUser.fName
        editUser.lName = last_name or editUser.lName
        editUser.email = email or editUser.email
        if password:
            editUser.password = password
        editUser.save()

        context["message"] = "Account Edited Successfully"
        return render(request, 'editAccount.html', context)

class UpdatePassword(View):
    def post(self, request):
        user = retrieveSessionID(request)
        if user is None:
            return redirect('/login/')
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
        if m is None or m.userType != "TA":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        assignments = Section.objects.filter(TA=m)
        return render(request, 'viewAssignments.html', {"assignments": assignments})

class ReadPublicContactInfoPage(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None:
            return redirect('/login/')
        search_query = request.GET.get('search', '')
        if search_query:
            users = User.objects.filter(
                Q(fName__icontains=search_query) | Q(lName__icontains=search_query) | Q(email__icontains=search_query)
            )
        else:
            users = User.objects.all()
        return render(request, 'readPublicContactInfo.html', {'users': users})

class InstructorViewCourses(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Instructor":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        courses = Class.objects.all()
        sections = Section.objects.all()
        
        for section in sections:
            schedule_parts = section.schedule.split(';')
            days = schedule_parts[0].replace('Days: ', '')
            time = schedule_parts[1].replace('Time: ', '')
            start_date = datetime.strptime(schedule_parts[2].replace('Start Date: ', '').strip(), '%Y-%m-%d').strftime('%m/%d/%Y')
            end_date = datetime.strptime(schedule_parts[3].replace('End Date: ', '').strip(), '%Y-%m-%d').strftime('%m/%d/%Y')
            
            section.formatted_schedule = f"Meets on {days} at {time}\nFrom {start_date} to {end_date}"
            
        return render(request, 'viewInstructorCourses.html', {
            "courses": courses,
            "sections": sections
        })

class AdminViewAllAssignments(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})

        courses = Class.objects.select_related('instructor').prefetch_related(
            Prefetch('section_set', queryset=Section.objects.select_related('TA'))
        ).all()

        for course in courses:
            for section in course.section_set.all():
                schedule_parts = section.schedule.split(';')
                days = schedule_parts[0].replace('Days: ', '')
                time = schedule_parts[1].replace('Time: ', '')
                start_date = datetime.strptime(schedule_parts[2].replace('Start Date: ', '').strip(), '%Y-%m-%d').strftime('%m/%d/%Y')
                end_date = datetime.strptime(schedule_parts[3].replace('End Date: ', '').strip(), '%Y-%m-%d').strftime('%m/%d/%Y')
                section.formatted_schedule = f"Meets on {days} at {time}\nFrom {start_date} to {end_date}"
                
        return render(request, 'viewAllAssignments.html', {
            "courses": courses
        })

class DeleteAssignment(View):
    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        
        section_id = request.POST.get("section_id")
        try:
            section = Section.objects.get(sectionId=section_id)
            section.delete()
            return redirect('/viewallassignments/')
        except Section.DoesNotExist:
            return render(request, 'viewAllAssignments.html', {"message": "Assignment not found"})

class DeleteCourse(View):
    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        
        course_id = request.POST.get("course_id")
        try:
            course = Class.objects.get(id=course_id)
            course.delete()
            return redirect('/viewallassignments/')
        except Class.DoesNotExist:
            return render(request, 'viewAllAssignments.html', {"message": "Course not found"})

class NotifyTAs(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType not in ["Admin", "Instructor"]:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        
        tas = User.objects.filter(userType='TA')
        return render(request, 'notifyTAs.html', {'tas': tas})

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType not in ["Admin", "Instructor"]:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        
        selected_tas = request.POST.getlist('selected_tas[]')
        message_content = request.POST.get('message')
        
        if not selected_tas:
            return render(request, 'notifyTAs.html', {
                'tas': User.objects.filter(userType='TA'),
                'error': 'Please select at least one TA'
            })
        
        if not message_content:
            return render(request, 'notifyTAs.html', {
                'tas': User.objects.filter(userType='TA'),
                'error': 'Message cannot be empty'
            })

        for ta_id in selected_tas:
            try:
                ta = User.objects.get(id=ta_id)
                Message.objects.create(
                    sender=m,
                    recipient=ta,
                    content=message_content
                )
            except User.DoesNotExist:
                continue

        return render(request, 'notifyTAs.html', {
            'tas': User.objects.filter(userType='TA'),
            'success': 'Messages sent successfully!'
        })

class NotifyUsers(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        
        users = User.objects.filter(userType__in=['TA', 'Instructor'])
        return render(request, 'notifyUsers.html', {'users': users})

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType != "Admin":
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        
        user_type = request.POST.get('user_type')
        selected_users = request.POST.getlist('selected_users[]')
        message_content = request.POST.get('message')
        
        if not selected_users:
            return render(request, 'notifyUsers.html', {
                'users': User.objects.filter(userType__in=['TA', 'Instructor']),
                'error': 'Please select at least one user'
            })
        
        if not message_content:
            return render(request, 'notifyUsers.html', {
                'users': User.objects.filter(userType__in=['TA', 'Instructor']),
                'error': 'Message cannot be empty'
            })

        for user_id in selected_users:
            try:
                user = User.objects.get(id=user_id)
                if user_type == 'both' or user.userType == user_type:
                    Message.objects.create(
                        sender=m,
                        recipient=user,
                        content=message_content
                    )
            except User.DoesNotExist:
                continue

        return render(request, 'notifyUsers.html', {
            'users': User.objects.filter(userType__in=['TA', 'Instructor']),
            'success': 'Messages sent successfully!'
        })

class ViewMessages(View):
    def get(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType not in ["TA", "Instructor"]:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        
        messages = Message.objects.filter(recipient=m).order_by('-timestamp')
        return render(request, 'viewMessages.html', {'messages': messages})

    def post(self, request):
        m = retrieveSessionID(request)
        if m is None or m.userType not in ["TA", "Instructor"]:
            return render(request, 'userNoAccess.html', {"message": "User Cannot Access This Page"})
        
        message_id = request.POST.get('message_id')
        if message_id:
            try:
                message = Message.objects.get(id=message_id, recipient=m)
                message.is_read = True
                message.save()
            except Message.DoesNotExist:
                pass
        
        return redirect('/viewmessages/')

def addUser(first_name, last_name, midI, userType, email, password):
    User.objects.create(
        fName=first_name or "First",
        lName=last_name or "Last",
        MidInit=midI or "",
        email=email,
        password=password or "password",
        userType=userType or "User"
    )

def createSection(request, section_name, instructor_id, schedule, course_id, max_capacity):
    instructor = User.objects.get(id=instructor_id)
    course = Class.objects.get(id=course_id)
    Section.objects.create(
        section_name=section_name,
        classId=course,
        TA=instructor,
        schedule=schedule,
        max_capacity=int(max_capacity)
    )
