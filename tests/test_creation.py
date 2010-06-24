try:
    import unittest2 as unittest
except ImportError:
    import unittest

from os import environ
from datetime import datetime, timedelta
from webtest import TestApp
from google.appengine.api.users import User
from pages import Contest, application

class CreationTestCase(unittest.TestCase):
    def setUp(self):
        self.clear_datastore()
        self.logout()
    
    def clear_datastore(self):
        # Use a fresh stub datastore.
        from google.appengine.api import apiproxy_stub_map
        from google.appengine.api import datastore_file_stub
        
        #apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        #stub = datastore_file_stub.DatastoreFileStub("appid", "/dev/null", "/dev/null")
        #apiproxy_stub_map.apiproxy.RegisterStub("datastore_v3", stub)
        apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map["datastore_v3"].Clear()
    def login(self, email="test@somewhere.com", admin=False):
        #environ["USER_IS_ADMIN"] = str(int(bool(admin)))
        environ["USER_IS_ADMIN"] = ("1" if admin else "0")
        environ["USER_EMAIL"] = email
        return User(email=email)
    def logout(self):
        fields = [
            "USER_IS_ADMIN",
            "USER_EMAIL",
            "USER_ID",
            "FEDERATED_IDENTITY",
            "FEDERATED_PROVIDER",
        ]
        
        for field in fields:
            try:
                del environ[field]
            except KeyError:
                pass
    
    def test_index(self):
        app = TestApp(application)
        response = app.get("/")
        print response
        self.assertIn("Create", response)
    
    def test_model(self):
        user = User(email="test@foo.com")
        Contest(creator = user).put()
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.creator, user)
    
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

