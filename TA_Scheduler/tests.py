from django.test import TestCase, Client
from .models import User, userPublicInfo, userPrivateInfo, Class, Section

class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        testUser = User(id=1, password=1234)
        testUserContact = userPublicInfo(id=1, email="testUser@uwm.edu")
        testUser.save()
        testUserContact.save()