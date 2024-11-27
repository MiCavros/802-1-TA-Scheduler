from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    userType = models.CharField(max_length=10)
    fName = models.CharField(max_length=50)
    lName = models.CharField(max_length=50)
    MidInit = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
testAdmin = User(fName = "Test", lName = "Admin", id = 1, userType = "Admin", email = "testadmin@uwm.edu", password = "1234" )


class userPublicInfo(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    workPhone = models.IntegerField
    officeHours = models.DateField

class userPrivateInfo(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    cellPhone = models.IntegerField
    address = models.CharField(max_length=50)

class Class(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    id = models.IntegerField(primary_key=True)
    location = models.CharField(max_length=50)
    time = models.DateTimeField
    ##labList =
    ##TAList =
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Section(models.Model):
    sectionId = models.IntegerField(primary_key=True)
    classId = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    TA = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


