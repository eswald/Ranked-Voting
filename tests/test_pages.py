from pages import Contest, application
from tests import VotingTestCase
from webtest import TestApp

class RootTestCase(VotingTestCase):
    def test_index(self):
        app = TestApp(application)
        response = app.get("/")
        print response
        self.assertIn("Create", response)

class ContestTestCase(VotingTestCase):
    def test_title(self):
        # The contest's title should be displayed on its main page.
        slug = "abcd"
        title = "Yet another design contest"
        Contest(slug=slug, title=title).put()
        app = TestApp(application)
        response = app.get("/" + slug)
        print response
        self.assertIn(title, response)

