from datetime import datetime, timedelta
from itertools import count, izip
from voting.models import Candidate, Election, Vote
from pages import application, db
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
        candidates = [
            "Favorite",
            "Middling",
            "Underdog",
        ]
        
        self.candidates = []
        for title in candidates:
            candidate = Candidate(title=title, parent=self.contest)
            candidate.put()
            self.candidates.append(str(candidate.key().id()))
        
        candidates = db.GqlQuery("SELECT * FROM Candidate WHERE ANCESTOR IS :1", self.contest)
        self.assertEqual(set(str(c.key().id()) for c in candidates), set(self.candidates))
        
        self.user = self.login()
        self.app = TestApp(application)
        self.page = self.app.get("/"+self.contest.key().name()+"/vote")
    
    def vote(self, ranks):
        for item_id in ranks:
            self.page.form.set("c"+item_id, ranks[item_id])
        self.page.form.submit()
        return Vote.get_by_key_name(self.contest.key().name()+"/"+str(self.user.user_id()))
    
    def test_vote_user(self):
        vote = self.vote(dict(izip(self.candidates, count(2))))
        self.assertEquals(vote.voter, self.user)
    
    def test_vote_election(self):
        vote = self.vote(dict(izip(self.candidates, count(2))))
        self.assertEquals(vote.election.key(), self.contest.key())
    
    def test_vote_ranked(self):
        expected = str.join(";", self.candidates)
        vote = self.vote(dict(izip(self.candidates, count(2))))
        self.assertEquals(vote.ranks, expected)
    
    def test_voting_equal(self):
        expected = str.join(",", self.candidates)
        vote = self.vote(dict.fromkeys(self.candidates, 2))
        self.assertEquals(vote.ranks, expected)
    
    def test_voting_mixed(self):
        first, second, third = self.candidates
        expected = second+","+third+";"+first
        vote = self.vote({first: 4, second: 2, third: 2})
        self.assertEquals(vote.ranks, expected)
    
    def test_voting_with_unranked(self):
        first, second, third = self.candidates
        expected = second+";"+third
        vote = self.vote({first: 0, second: 2, third: 4})
        self.assertEquals(vote.ranks, expected)
    
    def test_voting_all_unranked(self):
        vote = self.vote(dict.fromkeys(self.candidates, 0))
        self.assertIsNone(vote)

