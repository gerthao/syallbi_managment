import unittest
from google.appengine.ext import testbed
import jinja2
import webtest
import webapp2
from webapp2_extras.securecookie import SecureCookieSerializer
import mock
from google.appengine.ext import ndb
from Handlers import Calendar
from Handlers import DBM
from Handlers import Base
import time
from datetime import date


class CalendarTests(unittest.TestCase):
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
            ('/syllabusStepCalendar.html', Calendar.CalendarHandler),
            ('/deleteCalendarEntry', Calendar.DeleteCalendarEntryHandler),
            ('/updateCalendarEntries', Calendar.UpdateCalendarEntriesHandler)
        ], debug=True, config=sessionConfig)

        self.testapp = webtest.TestApp(app)

        # TODO: replace this with a parser mock once the parser is integrated
        # This is used to verify functionality in tests that are not testing entry's results
        # Entry is tested separately, and these responses allows further test isolation
        self.start_date = date(2015, 8, 1)
        self.end_date = date(2016, 2, 1)
        self.days_of_week = [0, 2, 4]
        self.entry_response = Calendar.generateEntryRange(self.start_date, self.end_date, self.days_of_week)

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

    def testGetCurrentCalendarWhenEmpty(self):
        expectedResult = DBM.Calendar(key=ndb.Key(self.syllabusName, 'calendar name', 'Calendar', 3),
                                      entries=self.entry_response,
                                      name=u'MyTestSyllabus')

        result = Calendar.getCurrentCalendar(self.syllabusName)
        assert (result == expectedResult)

    def testGetCurrentCalendarSyllabusLinkage(self):
        expectedResult = ndb.Key(self.syllabusName, 'calendar name', 'Calendar', 3)

        Calendar.getCurrentCalendar(self.syllabusName)

        result = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.syllabusName)).fetch(1)[0].calendar

        assert (result == expectedResult)

    def testGetCurrentCalendarWhenPopulated(self):
        expectedResult = DBM.Calendar(key=ndb.Key(self.syllabusName, 'calendar name', 'Calendar', 3),
                                      entries=self.entry_response,
                                      name=u'MyTestSyllabus')

        Calendar.getCurrentCalendar(self.syllabusName)
        result = Calendar.getCurrentCalendar(self.syllabusName)
        assert (result == expectedResult)

    def testGetCalendarPageCallsWithEmptyCalendar(self):
        # overwrite existing session values
        session = {'username': 'rock', 'currentPassword': 'cafe', 'currentSyllabus': self.syllabusName}

        # prepare the session cookie to be used
        serialized = self.secure_cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}

        # get the savePolicy page and submit information
        with mock.patch('jinja2.Template.render') as r2r:
            response = self.testapp.get("/syllabusStepCalendar.html", headers=headers)

            r2r.assert_called_with(
                {'progress': 7, 'weekdayPrinter': Calendar.weekdayPrinter, 'date_events': self.entry_response})

    def testGenerateEntryRange(self):
        startDate = date(2015, 1, 5)
        endDate = date(2015, 1, 12)
        daysWeek = [1, 3]

        expectedResult = [DBM.DateEvent(date=date(2015, 1, 6), event="", homework=""),
                          DBM.DateEvent(date=date(2015, 1, 8), event="", homework="")]

        result = Calendar.generateEntryRange(startDate, endDate, daysWeek)

        assert (result == expectedResult)

    def testDeleteCalendarEntry(self):
        startDate = date(2015, 1, 14)
        endDate = date(2015, 1, 15)
        daysWeek = [2]

        # overwrite existing session values
        session = {'username': 'rock', 'currentPassword': 'cafe', 'currentSyllabus': self.syllabusName}

        # prepare the session cookie to be used
        serialized = self.secure_cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}

        calendar = Calendar.getCurrentCalendar(self.syllabusName)
        calendar.entries = Calendar.generateEntryRange(startDate, endDate, daysWeek)
        calendar.put()

        # there should be one entry in the calendar entries at this point
        assert (calendar.entries == [DBM.DateEvent(date=startDate, event="", homework="")])

        self.testapp.post("/deleteCalendarEntry?toRemove=2015-01-14", headers=headers)

        # get the savePolicy page and submit information
        with mock.patch('jinja2.Template.render') as r2r:
            result = self.testapp.get("/syllabusStepCalendar.html", headers=headers)

            # not there shouldn't be any entries in the current calendar
            r2r.assert_called_with({'progress': 7, 'weekdayPrinter': Calendar.weekdayPrinter, 'date_events': []})

    def testSaveCalendarEntry(self):
        startDate = date(2015, 1, 14)
        endDate = date(2015, 1, 15)
        daysWeek = [2]
        testHW = "my homework"
        testEvent = "my event"

        expectedDateEvent = [DBM.DateEvent(date=startDate, event=testEvent, homework=testHW)]

        # overwrite existing session values
        session = {'username': 'rock', 'currentPassword': 'cafe', 'currentSyllabus': self.syllabusName}

        # prepare the session cookie to be used
        serialized = self.secure_cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}

        calendar = Calendar.getCurrentCalendar(self.syllabusName)
        calendar.entries = Calendar.generateEntryRange(startDate, endDate, daysWeek)
        calendar.put()

        # there should be one entry in the calendar entries at this point
        assert (calendar.entries == [DBM.DateEvent(date=startDate, event="", homework="")])

        params = {'homework': [testHW], 'event': [testEvent]}
        self.testapp.post("/updateCalendarEntries", params=params, headers=headers)

        # get the savePolicy page and submit information
        with mock.patch('jinja2.Template.render') as r2r:
            result = self.testapp.get("/syllabusStepCalendar.html", headers=headers)

            # not there shouldn't be any entries in the current calendar
            r2r.assert_called_with(
                {'progress': 7, 'weekdayPrinter': Calendar.weekdayPrinter, 'date_events': expectedDateEvent})

    def testGetClassesAndDays(self):
        goodDate = date(2015, 1, 1)
        badDate = date(2015, 2, 1)

        # syllabus I want to hit
        toHit = DBM.Syllabus(active=True, course=DBM.Course(department="cs", course_number=101, section_number=1))
        cal1 = DBM.Calendar(entries=[DBM.DateEvent(date=goodDate, event="")], daysActive=[3])
        cal1.put()
        toHit.calendar = cal1.key
        toHit.put()
        # syllabus I don't want to hit
        toMiss = DBM.Syllabus(active=True, course=DBM.Course(department="ab", course_number=102, section_number=2))
        cal2 = DBM.Calendar(entries=[DBM.DateEvent(date=badDate, event="")], daysActive=[3])
        cal2.put()
        toMiss.calendar = cal2.key
        toMiss.put()

        result = Calendar.getClasssesAndDays(goodDate, goodDate)

        assert (result == [[toHit]])

    def testAddDate(self):
        goodDate = date(2015, 1, 1)
        calendarName = "testCal"
        calendar = DBM.Calendar(parent=DBM.CalendarKey(calendarName), name=calendarName,
                                entries=[DBM.DateEvent(date=goodDate, event="")], daysActive=[0])
        calendar.put()
        toAddDate = date(2015, 1, 2)

        Calendar.addDateToCalendar(calendarName, toAddDate)

        calendar = DBM.Calendar.query(ancestor=DBM.CalendarKey(calendarName)).fetch()[0]

        assert (len(calendar.entries) == 2)
        assert (calendar.entries[1].date == toAddDate)

    def testCopyCalendar(self):
        calendarA = "A calendar"
        calendarB = "B calendar"

        ADate = DBM.DateEvent(date=date(2015, 1, 1), event="thing", homework="read")
        BDate = DBM.DateEvent(date=date(2015, 2, 3))

        DBM.Calendar(parent=DBM.CalendarKey(calendarA), name=calendarA, entries=[ADate]).put()
        DBM.Calendar(parent=DBM.CalendarKey(calendarB), name=calendarB, entries=[BDate]).put()

        Calendar.copyCalendar(calendarA, calendarB)

        calendarB = DBM.Calendar.query(ancestor=DBM.CalendarKey(calendarB)).fetch(1)[0]
        assert (calendarB.entries[0].event == ADate.event)
        assert (calendarB.entries[0].homework == ADate.homework)

        if __name__ == '__main__':
            unittest.main()
