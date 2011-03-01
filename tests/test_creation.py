from datetime import datetime, timedelta
from webtest import TestApp
from google.appengine.api.users import User
from pages import Contest, application
from tests import VotingTestCase

class UserTestCase(VotingTestCase):
    def test_user_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.creator, user)
    
    def test_user_ignored(self):
        # The save routine should ignore a submitted user parameter.
        user = self.login()
        email = "nobody@nowhere.com"
        other = User(email=email)
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd", "user": email})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.creator, user)

class CreationTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertAlmostEqual(fetched.created, datetime.now(), delta=timedelta(seconds=2))
    
    def test_creation_ignored(self):
        # The save routine should ignore a submitted created parameter.
        user = self.login()
        now = datetime.now()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd", "created": now + timedelta(days=2)})
        fetched = Contest.all().fetch(1)[0]
        self.assertAlmostEqual(fetched.created, datetime.now(), delta=timedelta(seconds=2))

class StartingTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertAlmostEqual(fetched.starts, datetime.now(), delta=timedelta(seconds=2))
    
    def test_explicit(self):
        user = self.login()
        app = TestApp(application)
        when = datetime(*(datetime.now() + timedelta(days=4, seconds=42)).timetuple()[:6])
        response = app.post("/create", params={"slug": "abcd", "starts": str(when)})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.starts, when)

class ClosingTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertGreater(fetched.closes, datetime.now() + timedelta(days=7))
    
    def test_explicit(self):
        user = self.login()
        app = TestApp(application)
        when = datetime(*(datetime.now() + timedelta(days=4, seconds=42)).timetuple()[:6])
        response = app.post("/create", params={"slug": "abcd", "closes": str(when)})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.closes, when)

class SlugTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.slug, "abcd")
    
    def test_form(self):
        # The creation form should fill in the slug properly.
        user = self.login()
        app = TestApp(application)
        page = app.get("/create")
        slug = "abcd"
        page.form.set("slug", slug)
        response = page.form.submit()
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.slug, slug)
    
    def test_conflict(self):
        slug = "abcd"
        Contest(slug=slug).put()
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": slug})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 1)
    
    def test_reserved_create(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "create"})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)
    
    def test_reserved_save(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "save"})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)
    
    def test_reserved_list(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "list"})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)
    
    def test_empty(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": ""})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)
    
    def test_omitted(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"title": "Yet Another Design Competition"})
        fetched = Contest.all().fetch(2)
        self.assertEqual(len(fetched), 0)
    
    def test_lowercased(self):
        request = "AbCd"
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": request})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.slug, request.lower())
    
    def test_punctuation(self):
        # The slug should replace punctuation with hyphens.
        request = "one and two, three and four; five"
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": request})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.slug, "one-and-two-three-and-four-five")
    
    def test_trimmed(self):
        # Spaces and hyphens should be trimmed from the ends of the slug.
        request = "-inner: "
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": request})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.slug, "inner")
    
    def test_numbers(self):
        # Periods should be allowed, particularly in numbers.
        request = "something-1.3"
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": request})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.slug, request)

class TitleTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        title = "Contest Title goes Here"
        response = app.post("/create", params={"slug": "abcd", "title": title})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, title)
    
    def test_form(self):
        # The creation form should fill in the title properly.
        user = self.login()
        app = TestApp(application)
        page = app.get("/create")
        title = "Contest Title goes Here"
        page.form.set("slug", "abcd")
        page.form.set("title", title)
        response = page.form.submit()
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, title)
    
    def test_trimmed(self):
        user = self.login()
        app = TestApp(application)
        title = " Contest Title goes Here\n"
        response = app.post("/create", params={"slug": "abcd", "title": title})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, title.strip())
    
    def test_default(self):
        # The title, if omitted, should default to the slug.
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, fetched.slug)
    
    def test_blank(self):
        # The title, if blank, should default to the slug.
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd", "title": ""})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.title, fetched.slug)

class PublicTestCase(VotingTestCase):
    def test_default(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.public, False)
    
    def test_form(self):
        # The creation form should have a checkbox for the public property.
        user = self.login()
        app = TestApp(application)
        page = app.get("/create")
        page.form.set("slug", "abcd")
        page.form.set("public", "1")
        response = page.form.submit()
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.public, True)
    
    def test_checked(self):
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd", "public": "1"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.public, True)
    
    def test_explicit(self):
        # An empty string for the public attribute is interpreted as false.
        user = self.login()
        app = TestApp(application)
        response = app.post("/create", params={"slug": "abcd", "public": ""})
        fetched = Contest.all().fetch(1)[0]
        self.assertEqual(fetched.public, False)

class DescriptionTestCase(VotingTestCase):
    def test_added(self):
        user = self.login()
        app = TestApp(application)
        description = "Contest Description goes Here"
        response = app.post("/create", params={"slug": "abcd", "description": description})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.description, description)
    
    def test_form(self):
        # The creation form should fill in the description properly.
        user = self.login()
        app = TestApp(application)
        page = app.get("/create")
        description = "Contest Description goes Here"
        page.form.set("slug", "abcd")
        page.form.set("description", description)
        response = page.form.submit()
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.description, description)
    
    def test_multiline(self):
        user = self.login()
        app = TestApp(application)
        description = "Contest Description goes Here.\nMore lines are explicitly allowed."
        response = app.post("/create", params={"slug": "abcd", "description": description})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.description, description)
    
    def test_trimmed(self):
        user = self.login()
        app = TestApp(application)
        description = " Contest Description goes Here\n"
        response = app.post("/create", params={"slug": "abcd", "description": description})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.description, description.strip())
    
    def test_default(self):
        # The description has something resembling a reasonable default.
        user = self.login()
        app = TestApp(application)
        default = "Created by " + user.nickname()
        response = app.post("/create", params={"slug": "abcd"})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.description, default)
    
    def test_blank(self):
        # The description, if blank, should default to the slug.
        user = self.login()
        app = TestApp(application)
        default = "Created by " + user.nickname()
        response = app.post("/create", params={"slug": "abcd", "description": ""})
        fetched = Contest.all().fetch(1)[0]
        self.assertEquals(fetched.description, default)

