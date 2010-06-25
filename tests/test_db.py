from google.appengine.api.users import User
from pages import Contest, application
from tests import VotingTestCase
from webtest import TestApp

class ContestTestCase(VotingTestCase):
    def test_model(self):
        user = User(email="test@foo.com")
        Contest(creator = user).put()
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.creator, user)

