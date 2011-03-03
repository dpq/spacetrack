import re
import logging
import os
from datetime import datetime, timedelta
from urllib2 import urlopen

from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

import tleutil
from model import Section, Object, TLE


def processSection(file, startwith, dt):
    logging.info("Processing section %s. Starting with %s. %d seconds left." % (file, startwith, (dt + timedelta(seconds = 10) - datetime.now()).seconds))
    orbiting = []
    startfound = (startwith == "")
    
    src = memcache.get("src_%s" % file).replace("\r", "").split("\n")
    logging.info("Web resource fetched. %d seconds left." % (dt + timedelta(seconds = 10) - datetime.now()).seconds)
    for i in range(0, len(src), tleutil.linecount):
        if len(src[i: i + tleutil.linecount]) < 3:
            break
        noradid, name, body, timestamp = tleutil.parseTLE(src[i: i + tleutil.linecount])
        if startfound and startwith == "":
            startwith = noradid
        if startwith == noradid:
            startfound = True
        if not startfound:
            continue
        
        #if memcache.get(key="name_%d" % noradid) is None:
        #    if Object.gql("where noradid = :1", noradid).count() == 0:
        obj = Object(noradid=noradid, name=name, section=file, orbiting=True)
        obj.put()
        logging.debug("New object %d (%s) discovered. %d seconds left." % (noradid, name, (dt + timedelta(seconds = 10) - datetime.now()).seconds))
        memcache.set(key="name_%d" % noradid, value=name, time=24*3600)
        
        #if TLE.gql("where noradid = :1 and timestamp = :2", noradid, timestamp).count() == 0:
        tle = TLE(noradid=noradid, section=file, body=body, timestamp=timestamp)
        tle.put()
        logging.debug("Writing new TLE for object %d. %d seconds left." % (noradid, (dt + timedelta(seconds = 10) - datetime.now()).seconds))
        memcache.set(key="tle_%d" % noradid, value=body, time=24*3600)
        
        orbiting.append(noradid)
        
        if dt + timedelta(seconds = 10) < datetime.now():
            for obj in Object.gql("where section = :1 and noradid < :2 and noradid > :3", file, noradid, startwith):
                if obj.noradid not in orbiting:
                    obj.orbiting = False
                    logging.debug("Object %d (%s) has decayed [1]. %d seconds left." % (obj.noradid, obj.name))
            logging.info("Section %s processor nearing expiration, returning at %d (%s)" % (file, noradid, name))
            return str(noradid)
    
    for obj in Object.gql("where section = :1 and noradid > :2", file, startwith):
        if obj.noradid not in orbiting:
            obj.orbiting = False
            logging.debug("Object %d (%s) has decayed [2] " % (obj.noradid, obj.name))
    logging.info("Section %s successfully processed." % file)
    return ""


def main():
    dt = datetime.now()
    logging.debug("New process spawned on %s" % str(dt))
    print 'Content-Type: text/plain'
    print ''

    section, last = os.environ['PATH_INFO'].replace("/updateContent/", "").split("/")
    logging.debug("Section and noradid specified, seeking (%s) in %s" % (last, section))

    logging.info("Working on %s. Starting with (%s)" % (section, last))
    last = processSection(section, last, dt)
    if last != "":
        logging.info("Spawning next update task for /updateContent/%s/%s" % (section, last))
        taskqueue.add(url="/updateContent/%s/%s" % (section, last), method='GET')
        return

    #taskqueue.add(url="/updateCount", method='GET')


if __name__ == "__main__":
    main()