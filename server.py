from datetime import datetime, timedelta
from urllib import unquote
from math import floor

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache
from django.utils import simplejson

import model


class Sections(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        res = { "featured.txt": "Featured" }
        for s in model.Section.gql("order by file asc"):
           res[s.file] = s.name
        self.response.out.write(simplejson.dumps(res))


class Satellites(webapp.RequestHandler):
    def get(self, sections):
        self.response.headers['Content-Type'] = 'text/plain'
        res = {}
        sections = unquote(sections).split(",")
        for section in sections:
            if section == "featured.txt":
                res[35865] = "METEOR-M"
                continue
            query = model.Object.gql("where section = :1 and orbiting = :2 order by noradid asc", section, True)
            while True:
                result = query.fetch(1000)
                for obj in result:
                    res[obj.noradid] = obj.name
                if len(result) < 1000:
                    break
                cursor = query.cursor()
                query.with_cursor(cursor)
        self.response.out.write(simplejson.dumps(res))


class TLE(webapp.RequestHandler):
    def get(self, satellites):
        self.response.headers['Content-Type'] = 'text/plain'
        res = []
        if satellites == "":
            return self.response.out.write(simplejson.dumps(res))
        satellites = unquote(satellites).split(",")
        if len(satellites) > 50:
            self.response.out.write(simplejson.dumps({}))
            return
        for sat in satellites:
            tle = memcache.get("tle_%s" % sat)
            if tle is None:
                tle = model.TLE.gql("where noradid = :1 order by timestamp desc", int(sat)).fetch(1)[0].body
                memcache.set(key="tle_%s" % sat, value=tle, time=24*3600)
            res.append(tle.split("\n"))
        self.response.out.write(simplejson.dumps(res))


class Name(webapp.RequestHandler):
    def get(self, satellite):
        self.response.headers['Content-Type'] = 'text/plain'
        res = memcache.get("name_%s" % satellite)
        if res is None:
            res = model.Object.gql("where noradid = :1", int(satellite)).fetch(1)[0].name
            memcache.set(key="name_%s" % satellite, value=res, time=24*3600)
        self.response.out.write(res)


class Icon(webapp.RequestHandler):
    def get(self, satellite):
        self.response.headers['Content-Type'] = 'text/plain'


class Age(webapp.RequestHandler):
    def get(self, sat):
        self.response.headers['Content-Type'] = 'text/plain'
        diff = datetime.utcnow() - model.TLE.gql("where noradid = :1 order by timestamp desc", int(sat)).fetch(1)[0].timestamp
        if diff.days > 2:
            dayStr = "days"
        else:
            dayStr = "day"
        if diff.seconds > 7200:
            hourStr = "hours"
        else:
            hourStr = "hour"
        if diff.days > 0:
            self.response.out.write("%d %s %d %s"%(diff.days, dayStr, floor(diff.seconds/3600), hourStr))
        elif diff.seconds > 3600:
            self.response.out.write("%d %s"%(floor(diff.seconds/3600), hourStr))
        else:
            self.response.out.write("Less than 1 hour")


class Count(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        count = memcache.get("count")
        if count is None:
            self.response.out.write("N/A")
        else:
            self.response.out.write(count)


#class Details(webapp.RequestHandler):
    #def get(self, int_id):
        #self.response.headers['Content-Type'] = 'text/html'
        #res = urlfetch.fetch(url="http://nssdc.gsfc.nasa.gov/nmc/spacecraftDisplay.do?id=" + int_id, deadline=10)
        #if res.status_code == 200:
          #self.response.out.write(res.content)


application = webapp.WSGIApplication([
    ('/directory/', Sections),
    (r'/directory/(.*)', Satellites),
    (r'/tle/(.*)', TLE),
    (r'/name/(.*)', Name),
    (r'/icon/(.*)', Icon),
    (r'/age/(.*)', Age),
#    (r'/details/(.*)', Details),
    ('/count', Count)
    ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()