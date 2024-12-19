from django.test import TestCase

from TA_Scheduler.main import createSection
from django import test

from TA_Scheduler.models import Class


class TestCreateSection(TestCase):
    def test_createSection(self):
        Class.objects.create(title='test')
        newSection = createSection("name", "schedule", 0, 1)
        self.assertEqual(newSection.section_name, "name")

    def test_noSchedule(self):
        self.assertEqual(createSection("name", "", 0, 1),False)

    def test_invalidSchedule(self):
        self.assertEqual(createSection("name", "Time :D", 0, 1),False)

    def test_invalidCourse(self):
        self.assertEqual(createSection("name", "schedule", 0, 1),False)

    def test_noCourse(self):
        self.assertEqual(createSection("name", "schedule", "", 1),False)

    def test_noCapacity(self):
        self.assertEqual(createSection("name", "schedule", 0, ""),False)

    def test_InvalidCapacity(self):
        self.assertEqual(createSection("name", "schedule", 0, 100000000),False)
