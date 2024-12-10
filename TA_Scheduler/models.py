from django.db import models
from datetime import date  # Import date

class User(models.Model):
    fName = models.CharField(max_length=50)
    lName = models.CharField(max_length=50)
    MidInit = models.CharField(max_length=1, null=True, blank=True)
    email = models.EmailField(unique=True, primary_key=True)
    password = models.CharField(max_length=50)
    userType = models.CharField(max_length=20)

class userPublicInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    email = models.EmailField(default="example@uwm.edu")
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

class userPrivateInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1) 
    dob = models.DateField(default=date(2000, 1, 1))

class Class(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    schedule = models.CharField(max_length=255)
    assignments = models.TextField(default="No assignments")
    location = models.CharField(max_length=100, null=True, blank=True)

class Section(models.Model):
    sectionId = models.AutoField(primary_key=True)
    section_name = models.CharField(max_length=100, default="Default Section")
    classId = models.ForeignKey(Class, on_delete=models.CASCADE)
    TA = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.CharField(max_length=255)
    max_capacity = models.IntegerField()