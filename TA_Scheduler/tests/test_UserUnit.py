from django.test import TestCase

from TA_Scheduler.main import addUser, retrieveEditUserID, editUser, deleteUser, editContactInfo
from TA_Scheduler.models import User
import unittest

class TestAddUser(TestCase):
    def test_addUser(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        self.assertEqual(User.objects.get(email="test@uwm.edu"), test_user)

    def test_noEmail(self):
        self.assertEqual(addUser("John", "Doe", "J", "TA", "", "testpassword"), False)

    def test_noPassword(self):
        self.assertEqual(addUser("John", "Doe", "J", "TA", "test@uwm.edu", ""), False)
    def test_noUserType(self):
        self.assertEqual(addUser("John", "Doe", "J", "", "test@uwm.edu", "testpassword"), False)

class TestEditUser(TestCase):
    def test_editUser(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        editUser(test_user, "Jane", "Doe", "test2@uwm.edu", "test1password")
        self.assertEqual(User.objects.get(email="test2@uwm.edu"), test_user)

    def test_InvalidEmail(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        self.assertEqual(editUser(test_user, "Jane", "Doe", "test2", "testpassword"), False)
    def test_samePassword(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        self.assertEqual(editUser(test_user, "Jane", "Doe", "test2@uwm.edu", "testpassword"), False)

    def test_blankName(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        self.assertEqual(editUser(test_user, "", "", "test2@uwm.edu", "testpassword"), False)

class testEditContact(TestCase):
    def test_editPhone(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        editContactInfo(test_user, "4142222222", "Address")
        self.assertEqual(test_user.phone, "4142222222")

    def test_editAddress(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        editContactInfo(test_user, "4142222222", "Address")
        self.assertEqual(test_user.address, "Address")

    def test_removePhone(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        editContactInfo(test_user, "4142222222", "Address")
        editContactInfo(test_user, "", "Address")
        self.assertEqual(test_user.phone, "")

    def test_removePhone(self):
        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
        editContactInfo(test_user, "4142222222", "Address")
        editContactInfo(test_user, "", "Address")
        self.assertEqual(test_user.phone, "")

#class TestDeleteUser(TestCase):
#    def test_deleteUser(self):
#        test_user = addUser("John", "Doe", "J", "TA", "test@uwm.edu", "testpassword")
#        deleteUser(test_user.id)
#        self.assertEqual(User.objects.get(email="test@uwm.edu"), None)

if __name__ == '__main__':
    unittest.main()