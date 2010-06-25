from pages import application
from tests import VotingTestCase
from webtest import TestApp

class RootTestCase(VotingTestCase):
    def test_index(self):
        app = TestApp(application)
        response = app.get("/")
        print response
        self.assertIn("Create", response)

