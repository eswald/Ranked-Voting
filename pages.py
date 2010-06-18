import cgi
from datetime import datetime, timedelta
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Contest(db.Model):
    creator = db.UserProperty()
    title = db.StringProperty()
    slug = db.StringProperty()
    description = db.StringProperty(multiline=True)
    started = db.DateTimeProperty(auto_now_add=True)
    closes = db.DateTimeProperty()

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
    def echo(self, message, *params):
        self.response.out.write(str(message) % params)

class MainPage(Page):
    def get(self):
        self.echo("""
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <title>Ranked-Pairs Contest Voting</title>
                </head>
                <body>
                    <h1>Contest Voting</h1>
                    <p>This site may be used for casual purposes only.</p>
                    <hr>
                    <p><a href="/create">Create a new contest!</a></p>
                </body>
            </html>
        """)

class ListPage(Page):
    def get(self):
        self.echo("""
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <title>Ranked-Pairs Contest List</title>
                </head>
                <body>
                    <h1>Contest Voting</h1>
                    <dl>
        """)
        
        current = Contest.gql("ORDER BY started DESC LIMIT 10")
        for contest in current:
            self.echo(
                """
                        <dt><a href="/contest/%s">%s</a></dt>
                        <dd>%s<br>%s - %s</dd>
                """,
                contest.slug,
                cgi.escape(contest.title),
                cgi.escape(contest.description),
                contest.started,
                contest.closes,
            )
        
        self.echo("""
                    </dl>
                    <hr>
                    <p><a href="/create">Create a new contest!</a></p>
                </body>
            </html>
        """)

class CreatePage(Page):
    def get(self):
        user = users.get_current_user()
        self.echo("""
            <html>
                <body>
                    <p>Hello, %s!</p>   
                    <form action="/save" method="post">
                        <table>
                            <tr><td>Title</td><td><input type="text" name="title"></td></tr>
                            <tr><td>Slug</td><td><input type="text" name="slug"></td></tr>
                            <tr><td>Description</td><td><textarea name="description">A short description for the front page.</textarea></td></tr>
                        </table>
                        <input type="submit" value="Submit">
                    </form>
                </body>
            </html>
        """, user.nickname())

class SavePage(Page):
    reserved = ["", "create", "save", "list", "admin"]
    def post(self):
        contest = Contest()
        contest.creator = users.get_current_user()
        contest.title = self.request.get("title").strip()
        contest.slug = self.request.get("slug").strip()
        contest.description = self.request.get("description").strip()
        contest.closes = datetime.now() + timedelta(days=14)
        contest.put()
        self.redirect("/")

class VotePage(Page):
    def get(self):
        user = users.get_current_user()
        self.response.headers['Content-Type'] = 'text/plain'
        self.echo('Hello, %s!\n', user.nickname())

class ContestPage(Page):
    def get(self):
        slug = self.request.url.split("/")[3]
        contest = Contest.gql("WHERE slug = :1 LIMIT 1", slug)[0]
        self.echo("""
            <html>
                <body>
                    <h1>%s</h1>
                    <p>%s</p>
                </body>
            </html>
        """, cgi.escape(contest.title), cgi.escape(contest.description))

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
