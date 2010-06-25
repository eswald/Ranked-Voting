from datetime import datetime, timedelta
from webtest import TestApp
from google.appengine.api.users import User
from pages import Contest, application
from tests import VotingTestCase

class UserTestCase(VotingTestCase):
    def test_user_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.creator, user)

class CreationTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertAlmostEqual(fetched.created, datetime.now(), delta=timedelta(seconds=2))

class StartingTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertAlmostEqual(fetched.starts, datetime.now(), delta=timedelta(seconds=2))
    
    def test_explicit(self):
        user = self.login()
        app = TestApp(application)
        when = datetime(*(datetime.now() + timedelta(days=4, seconds=42)).timetuple()[:6])
        response = app.post("/save", params={"slug": "abcd", "starts": str(when)})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.starts, when)

class ClosingTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertGreater(fetched.closes, datetime.now() + timedelta(days=7))
    
    def test_explicit(self):
        user = self.login()
        app = TestApp(application)
        when = datetime(*(datetime.now() + timedelta(days=4, seconds=42)).timetuple()[:6])
        response = app.post("/save", params={"slug": "abcd", "closes": str(when)})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.closes, when)

class SlugTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.slug, "abcd")
    
    def test_conflict(self):
        slug = "abcd"
        Contest(slug=slug).put()
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": slug})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 1)
    
    def test_reserved(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": "save"})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)
    
    def test_empty(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/save", params={"slug": ""})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)

class TitleTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        title = "Contest Title goes Here"
        response = app.post("/save", params={"slug": "abcd", "title": title})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, title)
    
    def test_trimmed(self):
        user = self.login()
        app = TestApp(application)
        title = " Contest Title goes Here\n"
        response = app.post("/save", params={"slug": "abcd", "title": title})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, title.strip())

