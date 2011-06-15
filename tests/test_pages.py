from datetime import datetime, timedelta
from pages import Candidate, Election, Vote, application
from tests import VotingTestCase
from webtest import TestApp

class RootTestCase(VotingTestCase):
    def check_shown(self, shown, public=True, approved=True, closes=+1):
        slug = "abcd"
        title = "Yet another design contest"
        closing = datetime.now() + timedelta(days=closes)
        Election(key_name=slug, title=title, public=public, approved=approved, closes=closing).put()
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
        # Approved, currently-open elections should be listed on the front page.
        self.check_shown(shown=True, public=True, approved=True, closes=+1)
    
    def test_public_link(self):
        # Approved, currently-open elections should have a valid link on the front page.
        slug = "abcd"
        title = "Yet another design contest"
        closing = datetime.now() + timedelta(days=1)
        Election(key_name=slug, title=title, public=True, approved=True, closes=closing).put()
        app = TestApp(application)
        response = app.get("/")
        response.click(title)
        self.assertIn(title, response)
    
    def test_unapproved_unlisted(self):
        # Unapproved elections should never appear on the front page.
        self.check_shown(shown=False, public=True, approved=False)
    
    def test_nonpublic_unlisted(self):
        # Non-public elections should never appear on the front page.
        self.check_shown(shown=False, public=False, approved=False)
    
    def test_finished_unlisted(self):
        # Elections should never appear on the front page after they close.
        self.check_shown(shown=False, closes=-1)

class ElectionTestCase(VotingTestCase):
    def test_title(self):
        # The election's title should be displayed on its main page.
        slug = "abcd"
        title = "Yet another design contest"
        Election(key_name=slug, title=title).put()
        app = TestApp(application)
        response = app.get("/" + slug)
        print response
        self.assertIn(title, response)
    
    def test_unknown(self):
        # Unknown elections should result in 404 errors.
        slug = "unknown"
        app = TestApp(application)
        response = app.get("/" + slug, status=404)
        self.assertEqual("404 Not Found", response.status)
    
    def test_voting(self):
        slug = "abcd"
        contest = Election(key_name=slug, title="Yet another contest")
        contest.put()
        first = Candidate(title="Favorite", parent=contest)
        first.put()
        second = Candidate(title="Underdog", parent=contest)
        second.put()
        user = self.login()
        app = TestApp(application)
        page = app.get("/"+slug+"/vote")
        page.form.set("c"+str(first.key().id()), 2)
        page.form.set("c"+str(second.key().id()), 4)
        response = page.form.submit()
        fetched = Vote.all().fetch(1)[0]
        self.assertEquals(fetched.voter, user)
        self.assertEquals(fetched.election.key(), contest.key())
        self.assertEquals(fetched.ranks, str(first.key().id()) + ";" + str(second.key().id()))

