from unittest.mock import patch

from django.contrib.auth import login
from django.http import request
from django.shortcuts import redirect
from django.views import View

from TA_Scheduler.main import pageAuthenticate, loginAuthenticate, retrieveSessionID
from django.test import TestCase
import unittest
from TA_Scheduler.models import User


class TestPageAuthenticate(TestCase):
    def testAdminpageAdmin(self):
        admin = User.objects.create(userType="Admin", email="testadminuser@uwm.edu", password="2222")
        admin.save()
        self.assertEqual(pageAuthenticate(admin,"Admin"), True)
    def testAdminpageInstructor(self):
        Instructor = User.objects.create(userType="Instructor", email="testadminuser@uwm.edu", password="2222")
        Instructor.save()
        self.assertEqual(pageAuthenticate(Instructor,"Admin"), False)
    def testAdminpageTA(self):
        TA = User.objects.create(userType="TA", email="testadminuser@uwm.edu", password="2222")
        TA.save()
        self.assertEqual(pageAuthenticate(TA,"Admin"), False)

    def testInstructorpageAdmin(self):
        admin = User.objects.create(userType="Admin", email="testadminuser@uwm.edu", password="2222")
        admin.save()
        self.assertEqual(pageAuthenticate(admin,"Instructor"), True)
    def testInstructorpageInstructor(self):
        Instructor = User.objects.create(userType="Instructor", email="testadminuser@uwm.edu", password="2222")
        Instructor.save()
        self.assertEqual(pageAuthenticate(Instructor,"Instructor"), True)
    def testInstructorpageTA(self):
        TA = User.objects.create(userType="TA", email="testadminuser@uwm.edu", password="2222")
        TA.save()
        self.assertEqual(pageAuthenticate(TA,"Instructor"), False)

    def testTApageAdmin(self):
        admin = User.objects.create(userType="Admin", email="testadminuser@uwm.edu", password="2222")
        admin.save()
        self.assertEqual(pageAuthenticate(admin,"TA"), True)
    def testTApageInstructor(self):
        Instructor = User.objects.create(userType="Instructor", email="testadminuser@uwm.edu", password="2222")
        Instructor.save()
        self.assertEqual(pageAuthenticate(Instructor,"TA"), True)
    def testTApageTA(self):
        TA = User.objects.create(userType="TA", email="testadminuser@uwm.edu", password="2222")
        TA.save()
        self.assertEqual(pageAuthenticate(TA,"TA"), True)

    def testPageNOUSERTYPE(self):
        TA = User.objects.create(userType="", email="testadminuser@uwm.edu", password="2222")
        TA.save()
        self.assertEqual(pageAuthenticate(TA, "TA"), False)
    def testNoPageType(self):
        TA = User.objects.create(userType="TA", email="testadminuser@uwm.edu", password="2222")
        TA.save()
        self.assertEqual(pageAuthenticate(TA, ""), False)

class TestLoginAuthenticate(TestCase):
    def testSuccessfulLogin(self):
        TA = User.objects.create(userType="TA", email="testadminuser@uwm.edu", password="2222")
        TA.save()
        self.assertEqual(loginAuthenticate(TA.email, TA.password ), 3)
    def testBadPassword(self):
        TA = User.objects.create(userType="TA", email="testadminuser@uwm.edu", password="2222")
        TA.save()
        self.assertEqual(loginAuthenticate(TA.email, "1111" ), 2)
    def testNoUser(self):
        TA = User.objects.create(userType="TA", email="testadminuser@uwm.edu", password="2222")
        TA.save()
        self.assertEqual(loginAuthenticate("Email", "Password" ), 1)

class TestRetrieveSessionID(TestCase):
    pass