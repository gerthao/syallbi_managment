import datetime
import unittest
import jinja2
import mock
import webapp2
import webtest
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from webapp2_extras.securecookie import SecureCookieSerializer
from Handlers import Base
from Handlers import CoursePolicy
from Handlers import DBM


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
            ('/delinkPolicy', CoursePolicy.DelinkPolicyHandler),
            ('/deletePolicy', CoursePolicy.DeletePolicyHandler),
            ('/editPolicy', CoursePolicy.EditPolicyHandler),
            ('/linkPolicy', CoursePolicy.LinkPolicyHandler),
            ('/syllabusStepPoliciesEditor.html', CoursePolicy.CoursePolicyEditHandler),
            ('/policyLib.html', CoursePolicy.PolicyLibHandler)
        ], debug=True, config=sessionConfig)

        self.testapp = webtest.TestApp(app)

        # create a test user
        newUser = DBM.User(parent=DBM.UserKey("rock"),
                           username="rock", password="cafe")
        newUser.put()

        # create a test syllabus
        self.syllabusKey = DBM.SyllabusKey("MyTestSyllabus")
        self.syllabusName = "MyTestSyllabus"
        newSyllabus = DBM.Syllabus(parent=self.syllabusKey, name=self.syllabusName,
                                   active=False)
        newSyllabus.put()

    def tearDown(self):
        self.testbed.deactivate()

    def testBadPolicyLinkSave(self):
        CoursePolicy.savePolicyToSyllabus("Good Header1", "", self.syllabusName)
        assert (len(DBM.Syllabus.query(ancestor=self.syllabusKey).fetch(1)[0].policies) == 0)
        CoursePolicy.savePolicyToSyllabus("", "Good Body", self.syllabusName)
        assert (len(DBM.Syllabus.query(ancestor=self.syllabusKey).fetch(1)[0].policies) == 0)
        CoursePolicy.savePolicyToSyllabus("", "", self.syllabusName)
        assert (len(DBM.Syllabus.query(ancestor=self.syllabusKey).fetch(1)[0].policies) == 0)

    def testGoodPolicyLinkSave(self):
        CoursePolicy.savePolicyToSyllabus("Good Header2", "Good Body", self.syllabusName)
        policies = DBM.Syllabus.query(ancestor=self.syllabusKey).fetch()[0].policies
        assert (len(policies) == 1)
        policy = DBM.Policy.query(ancestor=policies[0]).fetch()[0]
        assert (policy.head == "Good Header2")
        assert (policy.body == "Good Body")

    def testPolicyDelinkage(self):
        CoursePolicy.savePolicyToSyllabus("ToRemove", "Removal Body", self.syllabusName)
        beforeDelink = len(DBM.Syllabus.query(ancestor=self.syllabusKey).fetch(1)[0].policies)
        CoursePolicy.delinkPolicyFromSyllabus("ToRemove", self.syllabusName)
        afterDelink = len(DBM.Syllabus.query(ancestor=self.syllabusKey).fetch(1)[0].policies)
        assert (beforeDelink > afterDelink)

    def testPolicyDelete(self):
        CoursePolicy.savePolicy("ToDelete", "Removal Body")
        beforeDelete = len(DBM.Policy.query().fetch())
        CoursePolicy.deletePolicy("ToDelete")
        afterDelete = len(DBM.Policy.query().fetch())
        assert (beforeDelete > afterDelete)

    def testPolicySave(self):
        savedPolicy = CoursePolicy.savePolicy("CheckIfHere", "Removal Body")
        assert (len(DBM.Policy.query(ancestor=savedPolicy).fetch()) > 0)
        assert ((CoursePolicy.savePolicy("CheckIfHere", "Good Body")) == False)
        assert (len(DBM.Policy.query(ancestor=savedPolicy).fetch()) == 1)

    def testPolicyEdit(self):
        savedPolicy = CoursePolicy.savePolicy("EditThisGarbage", "FirstBody")
        CoursePolicy.editPolicy("EditThisGarbage", "SecondBody")
        assert (DBM.Policy.query(ancestor=savedPolicy).fetch()[0].body == "SecondBody")

    def testPolicyLinkage(self):
        savedPolicy = CoursePolicy.savePolicy("LinkThisGarbage", "FirstBody")
        beforeLink = len(DBM.Syllabus.query(ancestor=self.syllabusKey).fetch(1)[0].policies)
        CoursePolicy.linkPolicyToSyllabus("LinkThisGarbage", self.syllabusName)
        afterLink = len(DBM.Syllabus.query(ancestor=self.syllabusKey).fetch(1)[0].policies)
        assert (beforeLink < afterLink)

    def testSavePolicyCalls(self):
        # overwrite existing session values
        session = {'username': 'rock', 'currentPassword': 'cafe', 'currentSyllabus': self.syllabusName}

        # prepare the session cookie to be used
        serialized = self.secure_cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}

        # get the savePolicy page and submit information
        with mock.patch('jinja2.Template.render') as r2r:
            params = {'policyHeader': 'My New Head', 'policyBody': 'My New Body'}
            response = self.testapp.post("/syllabusStepPoliciesEditor.html", params, headers=headers)

            r2r.assert_not_called()

    def testGetPolicyStepCalls(self):
        # overwrite existing session values
        session = {'username': 'rock', 'currentPassword': 'cafe', 'currentSyllabus': self.syllabusName}

        # expected policy time
        now = datetime.datetime.utcnow()
        now = datetime.date(now.year, now.month, now.day)

        # prepare the session cookie to be used
        serialized = self.secure_cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}

        # get the savePolicy page and submit information
        with mock.patch('jinja2.Template.render') as r2r:
            response = self.testapp.get("/syllabusStepPoliciesEditor.html", headers=headers)

            r2r.assert_called_with({'progress': 6, 'importedPolicies': [], 'otherPolicies': []})

        with mock.patch('jinja2.Template.render') as r2r:
            CoursePolicy.savePolicyToSyllabus("LinkedTester", "my body", self.syllabusName)
            response = self.testapp.get("/syllabusStepPoliciesEditor.html", headers=headers)
            r2r.assert_called_with({'progress': 6,
                                    'importedPolicies': [
                                        DBM.Policy(key=ndb.Key('LinkedTester', 'policy header', 'Policy', 3),
                                                   body=u'my body',
                                                   head=u'LinkedTester',
                                                   updatedOn=now)],
                                    'otherPolicies': []})

        with mock.patch('jinja2.Template.render') as r2r:
            CoursePolicy.delinkPolicyFromSyllabus("LinkedTester", self.syllabusName)
            response = self.testapp.get("/syllabusStepPoliciesEditor.html", headers=headers)
            r2r.assert_called_with({'progress': 6,
                                    'importedPolicies': [],
                                    'otherPolicies': [
                                        DBM.Policy(key=ndb.Key('LinkedTester', 'policy header', 'Policy', 3),
                                                   body=u'my body',
                                                   head=u'LinkedTester',
                                                   updatedOn=now)]})

    def testGetPolicyLibCalls(self):
        # overwrite existing session values
        session = {'username': 'rock', 'currentPassword': 'cafe'}

        # expected time
        now = datetime.datetime.utcnow()
        now = datetime.date(now.year, now.month, now.day)

        # prepare the session cookie to be used
        serialized = self.secure_cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}

        # get the policyLib page and submit information
        with mock.patch('jinja2.Template.render') as r2r:
            response = self.testapp.get("/policyLib.html", headers=headers)

            r2r.assert_called_with({'editMode': False, 'policies': []})

        # ensure we can add policies and they'll show up in the library
        with mock.patch('jinja2.Template.render') as r2r:
            CoursePolicy.savePolicy("Stupid Policy", "No stupids")
            response = self.testapp.get("/policyLib.html", headers=headers)

            r2r.assert_called_with({'editMode': False,
                                    'policies': [
                                        DBM.Policy(key=ndb.Key('Stupid Policy', 'policy header', 'Policy', 3),
                                                   body=u'No stupids',
                                                   head=u'Stupid Policy',
                                                   updatedOn=now)
                                    ]})

        # ensure we can enter edit mode in the library1
        with mock.patch('jinja2.Template.render') as r2r:
            params = {'oldPolicyHead': 'Stupid Policy'}
            response = self.testapp.get("/editPolicy", params, headers=headers)

            r2r.assert_called_with({'oldPolicyBody': u'No stupids',
                                    'editMode': True,
                                    'oldPolicyHeader': u'Stupid Policy'})


if __name__ == '__main__':
    unittest.main()
