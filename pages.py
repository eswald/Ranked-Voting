import logging
from re import sub
from os.path import dirname, join
from datetime import datetime, timedelta
from dateutil.parser import parser as date_parser

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Contest(db.Model):
    creator = db.UserProperty()
    title = db.StringProperty()
    slug = db.StringProperty()
    description = db.StringProperty(multiline=True)
    created = db.DateTimeProperty(auto_now_add=True)
    starts = db.DateTimeProperty(auto_now_add=True)
    closes = db.DateTimeProperty()
    public = db.BooleanProperty(default=False)

class Entry(db.Model):
    sequence = db.IntegerProperty()
    title = db.StringProperty()
    description = db.StringProperty(multiline=True)

class Vote(db.Model):
    contest = db.ReferenceProperty(Contest)
    voter = db.UserProperty()
    ranks = db.ListProperty(long)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now_add=True)

class Page(webapp.RequestHandler):
    template_directory = join(dirname(__file__), "html")
    
    def echo(self, message, *params):
        self.response.out.write(str(message) % params)
    
    def render(self, template_name, **values):
        path = join(self.template_directory, template_name)
        self.response.out.write(template.render(path, values))
    
    def contest(self):
        slug = self.request.url.split("/")[3]
        query = Contest.gql("WHERE slug = :1 LIMIT 1", slug)
        try:
            contest = query[0]
        except IndexError:
            self.response.set_status(404, 'Not Found')
            contest = None
        return contest

class MainPage(Page):
    def get(self):
        now = datetime.now()
        current = Contest.gql("WHERE public = True AND closes > :1 ORDER BY closes LIMIT 10", now)
        self.render("index.html", contests=current)

class ListPage(Page):
    def get(self):
        current = Contest.gql("ORDER BY created DESC LIMIT 10")
        self.render("list.html", contests=current)

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
        try:
            contest = Contest()
            contest.creator = users.get_current_user()
            
            contest.slug = self._slugify(self.request.get("slug"))
            assert contest.slug not in self.reserved
            
            contest.title = self.request.get("title").strip() or contest.slug
            contest.public = bool(self.request.get("public"))
            
            default = "Created by " + contest.creator.nickname()
            contest.description = self.request.get("description").strip() or default
            
            when = self.request.get("starts")
            if when:
                contest.starts = date_parser().parse(when)
            else:
                contest.starts = datetime.now()
            
            when = self.request.get("closes")
            if when:
                contest.closes = date_parser().parse(when)
            else:
                contest.closes = contest.starts + timedelta(days=14)
            
            # Check for duplication as the absolute last thing before
            # inserting, for slightly better protection.
            # Consider rolling back if there are two of them after inserting.
            assert not list(db.GqlQuery("SELECT __key__ FROM Contest WHERE slug = :1 LIMIT 1", contest.slug))
            contest.put()
            self.redirect("/")
        except Exception as err:
            self.render("create.html", defaults=contest, error=err)
    
    def _slugify(self, request):
        slug = sub(r"[^a-z.0-9]+", "-", request.lower())
        return slug.strip("-")

class EntryPage(Page):
    def get(self):
        contest = self.contest()
        if not contest:
            return
        
        try:
            entries = db.GqlQuery("SELECT * FROM Entry WHERE ANCESTOR IS :1", contest)
        except db.KindError:
            entries = []
        
        self.render("newentry.html", contest=contest, options=entries)
    
    def post(self):
        contest = self.contest()
        if not contest:
            return
        
        try:
            entry = Entry(parent=contest)
            
            entry.title = self.request.get("title").strip()
            entry.description = self.request.get("description").strip()
            
            # Collect the sequence as the absolute last thing before
            # inserting, for slightly better protection.
            # Consider rolling back on duplicate sequences.
            try:
                others = db.GqlQuery("SELECT __key__ FROM Entry WHERE ANCESTOR IS :1", contest)
            except db.KindError:
                others = []
            entry.sequence = len(list(others)) + 1
            entry.put()
            self.redirect("/%s/entry" % contest.slug)
        except Exception as err:
            self.render("newentry.html", contest=contest, options=[], defaults=entry, error=err)
            raise

class VotePage(Page):
    def get(self):
        contest = self.contest()
        if not contest:
            return
        user = users.get_current_user()
        entries = db.GqlQuery("SELECT * FROM Entry WHERE ANCESTOR IS :1", contest)
        ranks = [[], entries, []]
        self.render("vote.html", contest=contest, ranks=ranks)
    
    def post(self):
        contest = self.contest()
        user = users.get_current_user()
        self.response.headers['Content-Type'] = 'text/plain'
        self.echo('Form: %r', self.request.params)

class ContestPage(Page):
    def get(self):
        contest = self.contest()
        if not contest:
            return
        self.render("contest.html", contest=contest)

application = webapp.WSGIApplication([
        ("/", MainPage),
        ("/create", CreatePage),
        ("/list", ListPage),
        ("/[\w.-]+/entry", EntryPage),
        ("/[\w.-]+/vote", VotePage),
        ("/[\w.-]+", ContestPage),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
