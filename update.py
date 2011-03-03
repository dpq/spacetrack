import re
import logging
import os
from datetime import datetime, timedelta
from urllib2 import urlopen

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import tleutil
from model import Section, Object, TLE


class Master(webapp.RequestHandler):
    def get(self):
        sections = self.parseIndex()
        for file in sections:
            if Section.gql("where file = :1", file).count() == 0:
                section = Section(file=file, name=sections[file])
                section.put()
                memcache.set(key=file, value=sections[file], time=192*3600)
            taskqueue.add(queue_name="download", url="/download/%s" % file, method='GET')


    def parseIndex(self):
        master = urlopen(tleutil.source + "index.asp").read()
        entries = re.findall('(?<=").+\.txt">[^<]+', master)
        sections = {}
        for e in entries:
            f, n = e.split('">')
            # Strip out the excessive whitespace chars and the occasional newline
            sections[f] = re.sub("\s+", " ", n.replace("\r", "").replace("\n", ""))
        return sections




class Download(webapp.RequestHandler):
    def get(self, file):
        source = urlopen(tleutil.source + file).read()
        memcache.set(key="src_%s" % file, value=source, time=24*3600)
        taskqueue.add(url="/update/%s/" % file, method='GET')




class Count(webapp.RequestHandler):
    def get(self):
        query = Object.gql("where orbiting = :1 order by noradid asc", True)
        count = 0
        while True:
            result = query.fetch(1000)
            count += len(result)
            if len(result) < 1000:
                break
            cursor = query.cursor()
            query.with_cursor(cursor)
        memcache.set(key='count', value=str(count), time=24*3600)




class File(webapp.RequestHandler):
    def get(self, section, last):
        dt = datetime.now()
        last = self.processSection(section, last, dt)
        if last != "":
            logging.info("Spawning next update task for /updateContent/%s/%s" % (section, last))
            taskqueue.add(url="/update/%s/%s" % (section, last), method='GET')
            return
        taskqueue.add(url="/counter", method='GET')


    def processSection(self, file, startwith, dt):
        logging.info("Working on section %s. Starting with '%s'." % (file, startwith))
        orbiting = []
        startfound = True
        if startwith != "":
            startwith = int(startwith)
            startfound = False
        
        src = memcache.get("src_%s" % file).replace("\r", "").split("\n")
        logging.debug("Resource %s fetched from cache." % file)
        for i in range(0, len(src), tleutil.linecount):
            if len(src[i: i + tleutil.linecount]) < 3:
                break
            noradid, name, body, timestamp = tleutil.parseTLE(src[i: i + tleutil.linecount])
            if startwith == "" and startfound:
                startwith = noradid
            if startwith == noradid:
                startfound = True
                continue
            if not startfound:
                continue
            
            if Object.gql("where noradid = :1 and section = :2", noradid, file).count() == 0:
                obj = Object(noradid=noradid, name=name, section=file, orbiting=True)
                obj.put()
                logging.debug("New object %d (%s) discovered." % (noradid, name))
            memcache.set(key="name_%d" % noradid, value=name, time=24*3600)
            
            if TLE.gql("where noradid = :1 and timestamp = :2", noradid, timestamp).count() == 0:
                tle = TLE(noradid=noradid, section=file, body=body, timestamp=timestamp)
                tle.put()
                logging.debug("Writing new TLE for object %d." % (noradid))
            memcache.set(key="tle_%d" % noradid, value=body, time=24*3600)
            
            orbiting.append(noradid)
            
            if dt + timedelta(seconds = 10) < datetime.now():
                for obj in Object.gql("where section = :1 and noradid < :2 and noradid > :3", file, noradid, startwith):
                    if obj.noradid not in orbiting:
                        obj.orbiting = False
                        obj.put()
                        logging.debug("Object %d (%s) has decayed." % (obj.noradid, obj.name))
                logging.info("Section %s processor nearing expiration, returning at %d (%s)" % (file, noradid, name))
                return str(noradid)
        
        for obj in Object.gql("where section = :1 and noradid > :2", file, startwith):
            if obj.noradid not in orbiting:
                obj.orbiting = False
                obj.put()
                logging.debug("Object %d (%s) has decayed." % (obj.noradid, obj.name))
        logging.info("Section %s successfully processed." % file)
        return ""




application = webapp.WSGIApplication([
    ('/update', Master),
    (r'/download/(.*)', Download),
    (r'/update/(.*)/(.*)', File),
    ('/counter', Count)
    ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()