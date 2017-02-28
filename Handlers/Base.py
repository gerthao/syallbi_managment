import jinja2
import webapp2
from webapp2_extras import sessions

import DBM

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./html'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)
        self.session_store = sessions.get_store(request=self.request)
        JINJA_ENVIRONMENT.globals['session'] = self.session

    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    def check_login(self):
        user = DBM.User.query(ancestor=DBM.UserKey(self.session.get('username'))).fetch(1)
        if len(user) == 0 or self.session.get('currentPassword') != user[0].password:
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render({}))
            self.redirect("/")
            return False
        return True

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()
