from datetime import datetime, timedelta
from pages import Contest, application
from tests import VotingTestCase
from webtest import TestApp

class RootTestCase(VotingTestCase):
    def check_shown(self, shown, public=True, closes=+1):
        slug = "abcd"
        title = "Yet another design contest"
        closing = datetime.now() + timedelta(days=closes)
        Contest(slug=slug, title=title, public=public, closes=closing).put()
        app = TestApp(application)
        response = app.get("/")
        print response
        if shown:
            self.assertIn(title, response)
            self.assertIn("/"+slug, response)
        else:
            self.assertNotIn(title, response)
            self.assertNotIn("/"+slug, response)
    
    def test_create_link(self):
        app = TestApp(application)
        response = app.get("/")
        print response
        self.assertIn("/create", response)
    
    def test_public_listed(self):
        # Public, currently-open contests should be listed on the front page.
        self.check_shown(shown=True, public=True, closes=+1)
    
    def test_public_link(self):
        # Public, currently-open contests should have a valid link on the front page.
        slug = "abcd"
        title = "Yet another design contest"
        closing = datetime.now() + timedelta(days=1)
        Contest(slug=slug, title=title, public=True, closes=closing).put()
        app = TestApp(application)
        response = app.get("/")
        response.click(title)
        self.assertIn(title, response)
    
    def test_nonpublic_unlisted(self):
        # Non-public contests should never appear on the front page.
        self.check_shown(shown=False, public=False)
    
    def test_finished_unlisted(self):
        # Contests should never appear on the front page after they close.
        self.check_shown(shown=False, closes=-1)

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
    
    def test_unknown(self):
        # Unknown contests should result in 404 errors.
        slug = "unknown"
        app = TestApp(application)
        response = app.get("/" + slug, status=404)
        self.assertEqual("404 Not Found", response.status)

