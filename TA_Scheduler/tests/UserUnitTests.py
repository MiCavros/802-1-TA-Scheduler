from django.test import TestCase

from TA_Scheduler.main import addUser, retrieveEditUserID, editUser, deleteUser
from TA_Scheduler.models import User
import unittest

class TestAddUser(TestCase):
    def test_addUser(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        self.assertEqual(User.objects.get(email="test@uwm.edu"), test_user)

class TestRetrieveEditUser(unittest.TestCase):
    def test_retrieveEditUserID(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        self.assertEqual(retrieveEditUserID("1"), test_user.id)

class TestEditUser(unittest.TestCase):
    def test_editUser(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        editUser(test_user.id, "Jane", "Doe", "J", "TA", "test2@uwm.edu", "testpassword")
        self.assertEqual(User.objects.get(email="test2@uwm.edu"), test_user.email)

class TestDeleteUser(unittest.TestCase):
    def test_deleteUser(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        deleteUser(test_user.id)
        self.assertEqual(User.objects.get(email="test@uwm.edu"), None)

if __name__ == '__main__':
    unittest.main()