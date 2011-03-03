from google.appengine.api import memcache
from google.appengine.ext import db

import model

def main():
    query = model.Object.gql("where orbiting = :1 order by noradid asc", True)
    count = 0
    while True:
        result = query.fetch(1000)
        count += len(result)
        if len(result) < 1000:
            break
        cursor = query.cursor()
        query.with_cursor(cursor)
    memcache.set(key='count', value=str(count), time=24*3600)

if __name__ == "__main__":
    main()