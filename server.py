from mako.template import Template
import cherrypy
import redis
class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        li = []
        count = 0
        r = redis.StrictRedis(host='localhost', port=6379, db=1)
        top_10_ids = r.sort("ids",start=0,num=10)
        for key in top_10_ids:
            li.append(r.hgetall(key))
            print(key)
        return Template(filename='index.html').render(data=li)
cherrypy.quickstart(HelloWorld())
