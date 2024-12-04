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

from TA_Scheduler.views import Login, Home, CreateUser, CreateCourse, manageUser, CreateSection, \
    editContactInfo, editAccount, assignSections, adminEditContactInfo
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', Login.as_view(), name='Login'),

    path('home/', Home.as_view(), name='Home'),

    path('createuser/', CreateUser.as_view(), name='Create User'),
    path('create-course/', CreateCourse.as_view(), name='Create Course'),
    path('editcontactinfo/', editContactInfo.as_view(), name='Edit Contact Info'),

    path('manageuser/', manageUser.as_view(), name='Manage Users'),
    path('createsection/', CreateSection.as_view(), name='Create Section'),
    path('editaccount/', editAccount.as_view(), name='Edit Account'),
    path('assignsections/', assignSections.as_view(), name='Assign Sections'),
    path('admineditcontactinfo/', adminEditContactInfo.as_view(), name='Admin Edit Contact Info'),
    path('delete-user/', views.delete_user, name='delete_user')
]
