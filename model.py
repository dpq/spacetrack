from google.appengine.ext import db

class Section(db.Model):
    file = db.StringProperty()
    name = db.StringProperty()


class Object(db.Model):
    noradid = db.IntegerProperty()
    name = db.StringProperty()
    section = db.StringProperty()
    orbiting = db.BooleanProperty()     # To track down decayed objects


class TLE(db.Model):
    noradid = db.IntegerProperty()
    timestamp = db.DateTimeProperty()
    body = db.TextProperty()