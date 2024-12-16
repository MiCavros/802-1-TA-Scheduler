"""
URL configuration for TA_Scheduler project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from TA_Scheduler.views import Login, Home, CreateUser, CreateCourse, manageUsers, CreateSection, \
    editContactInfo, editAccount, AssignSection, UpdatePassword, TaViewAssignmentsPage, ReadPublicContactInfoPage, \
    InstructorViewCourses, AdminViewAllAssignments, DeleteAssignment, DeleteCourse, NotifyTAs, ViewMessages, NotifyUsers
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', Login.as_view(), name='Login'),
    path('home/', Home.as_view(), name='Home'),

    path('createuser/', CreateUser.as_view(), name='Create User'),
    path('createcourse/', CreateCourse.as_view(), name='Create Course'),
    path('editcontactinfo/', editContactInfo.as_view(), name='Edit Contact Info'),
    path('manageusers/', manageUsers.as_view(), name='Manage Users'),
    path('createsection/', CreateSection.as_view(), name='Create Section'),
    path('editaccount/', editAccount.as_view(), name='Edit User'),
    path('assignsections/', AssignSection.as_view(), name='Assign Sections'),
    path('updatepassword/', UpdatePassword.as_view(), name='Update Password'),
    path('viewassignments/', TaViewAssignmentsPage.as_view(), name='View Assignments'),
    path('readpubliccontactinfo/', ReadPublicContactInfoPage.as_view(), name='read_public_contact_info'),
    path('instructor/viewcourses/', InstructorViewCourses.as_view(), name='Instructor View Courses'),
    path('viewallassignments/', AdminViewAllAssignments.as_view(), name='Admin View All Assignments'),
    path('deleteassignment/', DeleteAssignment.as_view(), name='Delete Assignment'),
    path('deletecourse/', DeleteCourse.as_view(), name='Delete Course'),
    path('notifytas/', NotifyTAs.as_view(), name='notify_tas'),
    path('viewmessages/', ViewMessages.as_view(), name='view_messages'),
    path('notifyusers/', NotifyUsers.as_view(), name='notify_users'),
]
