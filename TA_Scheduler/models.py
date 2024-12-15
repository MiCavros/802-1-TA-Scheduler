from django.db import models
from datetime import date

class User(models.Model):
    id = models.AutoField(primary_key=True)
    fName = models.CharField(max_length=50, default="First")
    lName = models.CharField(max_length=50, default="Last")
    MidInit = models.CharField(max_length=1, null=True, blank=True, default="")
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50, default="password")
    userType = models.CharField(max_length=20, default="User")

class userPublicInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(default="example@uwm.edu")
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

class userPrivateInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    dob = models.DateField(default=date(2000, 1, 1))

class Class(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    schedule = models.CharField(max_length=255)
    assignments = models.TextField(default="No assignments")
    location = models.CharField(max_length=100, null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="classes")


class Section(models.Model):
    sectionId = models.AutoField(primary_key=True)
    section_name = models.CharField(max_length=100, default="Default Section")
    classId = models.ForeignKey(Class, on_delete=models.CASCADE)
    TA = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    schedule = models.CharField(max_length=255)
    max_capacity = models.IntegerField()