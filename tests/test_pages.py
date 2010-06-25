from pages import Contest, application
from tests import VotingTestCase
from webtest import TestApp

class RootTestCase(VotingTestCase):
    def test_index(self):
        app = TestApp(application)
        response = app.get("/")
        print response
        self.assertIn("Create", response)
    
    def test_public_listed(self):
        # Public, currently-open contests should be listed on the front page.
        slug = "abcd"
        title = "Yet another design contest"
        Contest(slug=slug, title=title, public=True).put()
        app = TestApp(application)
        response = app.get("/")
        print response
        self.assertIn(title, response)
        self.assertIn("/"+slug, response)
    
    def test_nonpublic_unlisted(self):
        # Non-public contests should never appear on the front page.
        slug = "abcd"
        title = "Yet another design contest"
        Contest(slug=slug, title=title, public=False).put()
        app = TestApp(application)
        response = app.get("/")
        print response
        self.assertNotIn(title, response)
        self.assertNotIn("/"+slug, response)

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

