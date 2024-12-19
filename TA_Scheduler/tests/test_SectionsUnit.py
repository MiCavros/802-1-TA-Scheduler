from django.test import TestCase

from TA_Scheduler.main import createSection
from django import test

from TA_Scheduler.models import Class


class TestCreateSection(TestCase):
    def test_createSection(self):
        Class.objects.create(title='test')
        newSection = createSection("name", "schedule", 2, 1)
        self.assertEqual(newSection.section_name, "name")

