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
    contest = db.ReferenceProperty(Contest)
    sequence = db.IntegerProperty()
    title = db.StringProperty()
    url = db.StringProperty()
    votes = db.ListProperty(long)

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

class MainPage(Page):
    def get(self):
        current = Contest.gql("WHERE public = True ORDER BY created DESC LIMIT 10")
        self.render("index.html", contests=current)

class ListPage(Page):
    def get(self):
        current = Contest.gql("ORDER BY created DESC LIMIT 10")
        self.render("list.html", contests=current)

class CreatePage(Page):
    def get(self):
        user = users.get_current_user()
        self.render("create.html", user=user)

class SavePage(Page):
    reserved = ["", "create", "save", "list", "admin"]
    
    def post(self):
        try:
            contest = Contest()
            contest.creator = users.get_current_user()
            
            contest.slug = self._slugify(self.request.get("slug"))
            assert contest.slug not in self.reserved
            assert not list(Contest.gql("WHERE slug = :1 LIMIT 1", contest.slug))
            
            contest.title = self.request.get("title").strip() or contest.slug
            contest.description = self.request.get("description").strip()
            contest.public = bool(self.request.get("public"))
            
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
            
            contest.put()
            self.redirect("/")
        except Exception as err:
            self.render("create.html", defaults=contest, error=err)
    
    def _slugify(self, request):
        slug = sub(r"[^a-z.0-9]+", "-", request.lower())
        return slug.strip("-")

class VotePage(Page):
    def get(self):
        user = users.get_current_user()
        self.response.headers['Content-Type'] = 'text/plain'
        self.echo('Hello, %s!\n', user.nickname())

class ContestPage(Page):
    def get(self):
        slug = self.request.url.split("/")[3]
        contest = Contest.gql("WHERE slug = :1 LIMIT 1", slug)[0]
        self.render("contest.html", contest=contest)

application = webapp.WSGIApplication([
        ("/", MainPage),
        ("/create", CreatePage),
        ("/save", SavePage),
        ("/list", ListPage),
        ("/[\w.-]+", ContestPage),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
