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

from TA_Scheduler.views import Login, Home, CreateUser, CreateCourse, manageUser, CreateSection, editUser, \
    editContactInfo

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', Login.as_view(), name='Login'),

    path('home/', Home.as_view(), name='Home'),

    path('createuser/', CreateUser.as_view(), name='Create User'),
    path('createcourse/', CreateCourse.as_view(), name='Create Course'),
    path('editcontactinfo/', editContactInfo.as_view(), name='Edit Contact Info'),
    path('edituser/', editUser.as_view(), name='Edit User'),
    path('manageuser/', manageUser.as_view(), name='Mangage Users'),
    path('createsection/', CreateSection.as_view(), name='Create Section'),

]
