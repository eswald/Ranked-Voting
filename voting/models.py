from google.appengine.ext import db

class Election(db.Model):
    creator = db.UserProperty()
    title = db.StringProperty()
    description = db.StringProperty(multiline=True)
    created = db.DateTimeProperty(auto_now_add=True)
    starts = db.DateTimeProperty(auto_now_add=True)
    closes = db.DateTimeProperty()
    public = db.BooleanProperty(default=False)
    approved = db.BooleanProperty(default=False)

class Candidate(db.Model):
    title = db.StringProperty()
    description = db.StringProperty(multiline=True)

class Vote(db.Model):
    election = db.ReferenceProperty(Election, required=True)
    voter = db.UserProperty(required=True)
    ranks = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now_add=True)

