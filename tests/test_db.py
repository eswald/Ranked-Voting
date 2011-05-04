from google.appengine.api.users import User
from pages import Election, application
from tests import VotingTestCase
from webtest import TestApp

class ElectionTestCase(VotingTestCase):
    def test_model(self):
        user = User(email="test@foo.com")
        Election(creator = user).put()
        fetched = Election.all().fetch(1)[0]
        self.assertEquals(fetched.creator, user)

