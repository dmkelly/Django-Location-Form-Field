"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.forms import Form
from django.test import TestCase
from fields import LocationField, LocationWidget

class TestLocationField(TestCase):

    class TestForm(Form):
        location = LocationField()
    
    def test_make_field(self):
        self.TestForm()