from tornado import web

from iotDashboard import templates

class Index(web.RequestHandler):
    def get(self):
        self.render(templates + "/index.html")
