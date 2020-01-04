from mako.template import Template
import cherrypy
import redis
import os 

from datetime import datetime
class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        li = []
        count = 0
        r = redis.StrictRedis(host='localhost', port=6379, db=1)
        date = r.get('date')
        date_str = datetime.strptime(date, '%d%m%y').strftime("%b %d %Y")
        if date != datetime.now().strftime("%d%m%y"):
            os.system("python extract_and_dump_bhav_copy.py > script_std.log")
        top_10_ids = r.sort("keys",alpha=True,start=0,num=10)
        for key in top_10_ids:
            li.append(r.hgetall(key))
        return Template(filename='index.html').render(data=li,date=date_str)

    @cherrypy.expose
    def search(self, search_text):
        # cherrypy.request.method == 'GET'
        if not search_text or search_text == '*':
            return self.index()
        r = redis.StrictRedis(host='localhost', port=6379, db=1)
        date = r.get('date')
        date_str = datetime.strptime(date, '%d%m%y').strftime("%b %d %Y")
        keys = r.keys(pattern='*:*{0}*'.format(search_text.upper()))
        li=[]
        if keys:
            for key in keys:
                li.append(r.hgetall(key))
        return Template(filename='index.html').render(data=li,date=date_str)



cherrypy.quickstart(HelloWorld())
