import logging
from re import sub
from os.path import dirname, join
from collections import defaultdict
from itertools import repeat
from datetime import datetime, timedelta
from dateutil.parser import parser as date_parser
from random import choice

from google.appengine.api import users
from google.appengine.dist import use_library

# We need some 1.* features of the template system,
# particularly tuple unpacking in for loops.
use_library("django", "1.2")

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from voting import methods

class Election(db.Model):
    creator = db.UserProperty()
    title = db.StringProperty()
    description = db.StringProperty(multiline=True)
    created = db.DateTimeProperty(auto_now_add=True)
    starts = db.DateTimeProperty(auto_now_add=True)
    closes = db.DateTimeProperty()
    public = db.BooleanProperty(default=False)

class Candidate(db.Model):
    title = db.StringProperty()
    description = db.StringProperty(multiline=True)

class Vote(db.Model):
    election = db.ReferenceProperty(Election, required=True)
    voter = db.UserProperty(required=True)
    ranks = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now_add=True)

class Page(webapp.RequestHandler):
    template_directory = join(dirname(__file__), "html")
    
    def echo(self, message, *params):
        self.response.out.write(str(message) % params)
    
    def render(self, template_name, **values):
        path = join(self.template_directory, template_name)
        self.response.out.write(template.render(path, values))
    
    def election(self):
        slug = self.request.url.split("/")[3]
        election = Election.get_by_key_name(slug)
        if election is None:
            self.response.set_status(404, 'Not Found')
        return election

class MainPage(Page):
    def get(self):
        now = datetime.now()
        current = Election.gql("WHERE public = True AND closes > :1 ORDER BY closes LIMIT 10", now)
        self.render("index.html", elections=current)

class ListPage(Page):
    def get(self):
        current = Election.gql("ORDER BY created DESC LIMIT 10")
        self.render("list.html", elections=current)

class CreatePage(Page):
    reserved = [
        "",
        "create",
        "save",
        "list",
        "admin",
        "static",
        "favicon.ico",
    ]
    
    def get(self):
        user = users.get_current_user()
        self.render("create.html", user=user)
    
    def post(self):
        election = None
        try:
            slug = self._slugify(self.request.get("slug"))
            assert slug not in self.reserved
            
            election = Election(key_name=slug)
            election.creator = users.get_current_user()
            
            election.title = self.request.get("title").strip() or slug
            election.public = bool(self.request.get("public"))
            
            default = "Created by " + election.creator.nickname()
            election.description = self.request.get("description").strip() or default
            
            when = self.request.get("starts")
            if when:
                election.starts = date_parser().parse(when)
            else:
                election.starts = datetime.now()
            
            when = self.request.get("closes")
            if when:
                election.closes = date_parser().parse(when)
            else:
                election.closes = election.starts + timedelta(days=14)
            
            # Check for duplication as the absolute last thing before
            # inserting, for slightly better protection.
            # Consider rolling back if there are two of them after inserting.
            assert not Election.get_by_key_name(slug)
            election.put()
            self.redirect("/%s/candidate" % slug)
        except Exception, err:
            logging.exception("Failed to create election: %r", repr(locals()))
            self.render("create.html", defaults=election, error=err)
    
    def _slugify(self, request):
        slug = sub(r"[^a-z.0-9]+", "-", request.lower())
        return slug.strip("-")

class CandidatePage(Page):
    def get(self):
        election = self.election()
        if not election:
            return
        
        try:
            candidates = db.GqlQuery("SELECT * FROM Candidate WHERE ANCESTOR IS :1", election)
        except db.KindError:
            candidates = []
        
        self.render("candidate.html", election=election, candidates=candidates)
    
    def post(self):
        election = self.election()
        if not election:
            return
        
        try:
            candidate = Candidate(parent=election)
            
            candidate.title = self.request.get("title").strip()
            candidate.description = self.request.get("description").strip()
            
            candidate.put()
            self.redirect("/%s/candidate" % election.key().name())
        except Exception, err:
            logging.exception("Failed to save candidate: %r", repr(locals()))
            self.render("candidate.html", election=election, candidates=[], defaults=candidate, error=err)
            raise

class VotePage(Page):
    def get(self):
        election = self.election()
        if not election:
            return
        user = users.get_current_user()
        candidates = db.GqlQuery("SELECT * FROM Candidate WHERE ANCESTOR IS :1", election)
        vote = Vote.get_by_key_name(self._vote_key(election, user))
        if vote:
            entries = dict((c.key().id(), c) for c in candidates)
            keys = [[int(key) for key in rank.split(",")] for rank in vote.ranks.split(";")]
            ranks = self._interleave(repeat([]), ([entries[key] for key in rank] for rank in keys))
            unranked = [entries[key] for key in entries if key not in set(sum(keys, []))]
        else:
            ranks = [[]]
            unranked = candidates
        self.render("vote.html", election=election, ranks=ranks, unranked=unranked)
    
    def post(self):
        election = self.election()
        user = users.get_current_user()
        
        # Parse the form input into a reasonable vote set.
        ranks = defaultdict(set)
        for param in self.request.params:
            candidate = param[1:]
            if param[0] == "c" and candidate.isdigit():
                rank = self.request.get(param)
                ranks[rank].add(candidate)
        ranked = ";".join(",".join(sorted(ranks[key])) for key in sorted(ranks))
        
        # Todo: Use a single transaction for this whole thing,
        # folding the get_or_insert part into the transaction.
        vote = Vote.get_or_insert(self._vote_key(election, user),
            election=election, voter=user, ranks=ranked)
        if vote.ranks != ranked:
            vote.ranks = ranked
            vote.modified = datetime.now()
            vote.put()
        
        self.redirect("/%s/results" % election.key().name())
    
    def _vote_key(self, election, user):
        return "%s/%s" % (election.key().name(), user.user_id())
    
    @staticmethod
    def _interleave(*sequences):
        sequences = map(iter, sequences)
        while sequences:
            for seq in sequences:
                yield seq.next()

class ResultPage(Page):
    def get(self):
        election = self.election()
        if not election:
            return
        
        pieces = self.request.url.split("/")
        voting = dict((method.__name__, method) for method in methods.itervalues())
        try:
            method = pieces[5]
        except IndexError:
            method = choice(list(voting))
        
        candidates = db.GqlQuery("SELECT * FROM Candidate WHERE ANCESTOR IS :1", election)
        votes = db.GqlQuery("SELECT * FROM Vote WHERE election = :1", election)
        entries = dict((c.key().id(), c) for c in candidates)
        ballots = [([map(int, rank.split(",")) for rank in vote.ranks.split(";")], 1) for vote in votes]
        results = (map(entries.get, rank) for rank in voting[method](ballots, entries))
        methodnames = [(methods[key].__name__, key) for key in methods]
        self.render("election.html", election=election, ranks=results, methods=methodnames, method=method)

application = webapp.WSGIApplication([
        ("/", MainPage),
        ("/create", CreatePage),
        ("/list", ListPage),
        ("/[\w.-]+/candidate", CandidatePage),
        ("/[\w.-]+/vote", VotePage),
        ("/[\w.-]+/results", ResultPage),
        ("/[\w.-]+/results/\w*", ResultPage),
        ("/[\w.-]+", ResultPage),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
