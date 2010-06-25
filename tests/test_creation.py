from datetime import datetime, timedelta
from webtest import TestApp
from google.appengine.api.users import User
from pages import Contest, application
from tests import VotingTestCase

class CreationTestCase(VotingTestCase):
    def test_user_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.creator, user)
    
    def test_creation_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertAlmostEqual(fetched.created, datetime.now(), delta=timedelta(seconds=2))
    
    def test_starting_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertAlmostEqual(fetched.starts, datetime.now(), delta=timedelta(seconds=2))
    def test_starting_explicit(self):
        user = self.login()
        app = TestApp(application)
        when = datetime(*(datetime.now() + timedelta(days=4, seconds=42)).timetuple()[:6])
        response = app.post("/save", params={"slug": "abcd", "starts": str(when)})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.starts, when)
    
    def test_closing_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertGreater(fetched.closes, datetime.now() + timedelta(days=7))
    def test_closing_explicit(self):
        user = self.login()
        app = TestApp(application)
        when = datetime(*(datetime.now() + timedelta(days=4, seconds=42)).timetuple()[:6])
        response = app.post("/save", params={"slug": "abcd", "closes": str(when)})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.closes, when)
    
    def test_slug_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.slug, "abcd")
    def test_slug_conflict(self):
        slug = "abcd"
        Contest(slug=slug).put()
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": slug})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 1)
    def test_slug_reserved(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "save"})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)
    def test_slug_empty(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": ""})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)
    
    def test_title_added(self):
        user = self.login()
        app = TestApp(application)
        title = "Contest Title goes Here"
        response = app.post("/save", params={"slug": "abcd", "title": title})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, title)
    def test_title_trimmed(self):
        user = self.login()
        app = TestApp(application)
        title = " Contest Title goes Here\n"
        response = app.post("/save", params={"slug": "abcd", "title": title})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, title.strip())

