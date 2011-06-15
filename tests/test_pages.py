from datetime import datetime, timedelta
from pages import Candidate, Election, Vote, application, db
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

class VotePageTestCase(VotingTestCase):
    def setUp(self):
        super(VotingTestCase, self).setUp()
        self.contest = Election(key_name=self.id(), title="Yet another contest")
        self.contest.put()
        self.candidates = [
            Candidate(title="Favorite", parent=self.contest),
            Candidate(title="Underdog", parent=self.contest),
        ]
        
        for candidate in self.candidates:
            candidate.put()
        
        candidates = db.GqlQuery("SELECT * FROM Candidate WHERE ANCESTOR IS :1", self.contest)
        self.assertEqual(set(c.key().id for c in candidates), set(c.key().id for c in self.candidates))
        
        self.user = self.login()
        self.app = TestApp(application)
        self.page = self.app.get("/"+self.contest.key().name()+"/vote")
    
    def vote(self, ranks):
        for key in ranks:
            item_id = str(self.candidates[key].key().id())
            self.page.form.set("c"+item_id, ranks[key])
        self.page.form.submit()
        return Vote.get_by_key_name(self.contest.key().name()+"/"+str(self.user.user_id()))
    
    def test_vote_user(self):
        vote = self.vote({0: 2, 1: 4})
        self.assertEquals(vote.voter, self.user)
    
    def test_vote_election(self):
        vote = self.vote({0: 2, 1: 4})
        self.assertEquals(vote.election.key(), self.contest.key())
    
    def test_vote_ranked(self):
        expected = ";".join(str(c.key().id()) for c in self.candidates)
        vote = self.vote(dict((n, n+2) for n in range(len(self.candidates))))
        self.assertEquals(vote.ranks, expected)
    
    def test_voting_equal(self):
        expected = ",".join(str(c.key().id()) for c in self.candidates)
        vote = self.vote(dict((n, 2) for n in range(len(self.candidates))))
        self.assertEquals(vote.ranks, expected)

