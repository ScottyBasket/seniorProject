from django.test import TestCase
from http import HTTPStatus

from basset.models import Game, League, Location, Sport, Team
from eli.models import UserProfile

# Create your tests here.
class SportTestCase(TestCase):
    
    def setUp(self):
        pass