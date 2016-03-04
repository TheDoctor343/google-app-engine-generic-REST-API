"""Example for using the API Generator"""


import webapp2
import models
from google.appengine.api import users
import json
import logging


def login_required(handler_method):


    def wrapper(self, *args, **kwargs):

        user = users.get_current_user()

        if user:

            # Google login

            handler_method(self, *args, **kwargs)

        else:

            self.response.set_status(401)



    return wrapper


def key_obj(key):
    return dict(kind=key.kind(), id=key.id())


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        user = users.get_current_user()

        if user:
            self.redirect('/static/index.html#/')
        else:
            self.redirect(users.create_login_url(self.request.uri))


class GetUser(webapp2.RequestHandler):
    @login_required
    def get(self):

        user = users.get_current_user()

        obj = dict(email=user.email(), nickname=user.nickname())

        self.response.content_type = 'application/json'

        self.response.out.write(json.dumps(obj))

class TaskRequest(webapp2.RequestHandler):
    @login_required
    def get(self):
        logging.info(self.request.params)
        obj = models.API_GET(model_type=models.Task, key_method=models.Key_Method, request=self.request, kind="Task")

        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps(obj))

    @login_required
    def post(self):

        success, msg = models.API_POST(model_type=models.Task, key_method=models.Key_Method, request=self.request, kind="Task")

        if not success:
            self.response.set_status(400)
            self.response.write(msg)
        else:
            #obj = key_obj(msg)
            self.response.content_type = 'text/plain'
            self.response.out.write("It worked")

    @login_required
    def put(self):

        success, msg = models.API_PUT(model_type=models.Task, key_method=models.Key_Method, request=self.request, kind="Task")

        if not success:
            self.response.set_status(400)
            self.response.write(msg)
        else:
            self.response.set_status(200)

    @login_required
    def delete(self):

        success, msg = models.API_DELETE(model_type=models.Task, key_method=models.Key_Method, request=self.request, kind="Task")

        if not success:
            self.response.set_status(400)
            self.response.write(msg)
        else:
            self.response.set_status(200)


class Logout(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))







app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/user', GetUser),
    ('/task', TaskRequest),
    ('/dostuff', DoStuffForDebug),
    ('/logout', Logout)
], debug=True)
