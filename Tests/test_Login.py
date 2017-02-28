import unittest

import jinja2
import webapp2
import webtest
from google.appengine.ext import testbed
from webapp2_extras.securecookie import SecureCookieSerializer

from Handlers import Base
from Handlers import Login
from Handlers import Management


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        # create a cookie serializer to emulate our sessions
        self.secure_cookie_serializer = SecureCookieSerializer('no-one-will-guess-kwsfs-secret-key')
        sessionConfig = {}
        sessionConfig['webapp2_extras.sessions'] = {
            'secret_key': 'no-one-will-guess-kwsfs-secret-key',
        }
        # redirect Jinja Env to a directory up
        Base.JINJA_ENVIRONMENT = jinja2.Environment(
            loader=jinja2.FileSystemLoader('../html'),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True)

        # prepare env with only needed URLs
        app = webapp2.WSGIApplication([
            ('/', Login.LoginHandler),
            ('/manage.html', Management.ManagementHandler)
        ], debug=True, config=sessionConfig)

        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()

    def testGoodLogin(self):
        # overwrite existing session values
        session = {'username': 'user', 'currentPassword': 'pass'}

        # prepare the session cookie to be used
        serialized = self.secure_cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}

        # specify good information to be passed to the login method
        params = {'username': 'rock', 'password': 'cafe'}

        # get the login page and submit information
        self.testapp.get("/", headers=headers)
        response = self.testapp.post("/", params, headers=headers)

        # ensure user is redirected to management when a good login/pass is presented
        assert ("manage" in str(response))

    def testBadLogin(self):
        # overwrite existing session info and prepare cookie
        session = {'username': 'user', 'currentPassword': 'pass'}
        serialized = self.secure_cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}
        # bad params to be passed to login method
        params = {'username': 'r', 'password': 'c'}
        # get login page and submit bad information
        self.testapp.get("/", headers=headers)
        response = self.testapp.post("/", params, headers=headers)
        # ensure user goes back to the login page when a bad user/pass is presented
        assert ("302" in str(response))


if __name__ == '__main__':
    unittest.main()
