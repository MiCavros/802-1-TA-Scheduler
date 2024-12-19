from django.test import TestCase

from TA_Scheduler.main import createCourse


class TestCreateCourse(TestCase):
    def test_createCourse(self):
        course = createCourse("title", "description", "schedule", "location")
        self.assertEqual(course.title, "title")
    def test_noTitle(self):
        self.assertEqual(createCourse("", "description", "schedule", "location"), False)
    def test_noDescription(self):
        self.assertEqual(createCourse("title", "", "schedule", "location"), False)
    def test_noSchedule(self):
        self.assertEqual(createCourse("title", "description", "", "location"), False)
    def test_noLocation(self):
        self.assertEqual(createCourse("title", "description", "schedule", ""), False)