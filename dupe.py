from google.appengine.api import memcache
from google.appengine.ext import db

import model

def main():
    print "Content-Type: text/plain"
    print ""
    print "Dupes"
    query = model.Object.gql("where orbiting = :1 order by noradid asc", True)
    res = {}
    sects = {}
    while True:
        result = query.fetch(1000)
        for x in result:
            if res.has_key(x.noradid):
                res[x.noradid] += 1
                sects[x.noradid] += " " + x.section
            else:
                res[x.noradid] = 1
                sects[x.noradid] = x.section
        if len(result) < 1000:
            break
        cursor = query.cursor()
        query.with_cursor(cursor)
    for x in res:
        if res[x] > 1:
            s = sects[x].split()
            if len(s) > len(set(s)):
                print x, "::", res[x], " ", sects[x]

if __name__ == "__main__":
    main()