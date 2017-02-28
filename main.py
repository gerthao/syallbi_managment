#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys
sys.path.insert(0, 'libs')

import webapp2

from Handlers import Assessment
from Handlers import Calendar
from Handlers import CompletedSyllabus
from Handlers import Completion
from Handlers import CourseNumber
from Handlers import CoursePolicy
from Handlers import Department
from Handlers import GradeScale
from Handlers import InstructorStep
from Handlers import Login
from Handlers import Management
from Handlers import Schedule
from Handlers import Scraper
from Handlers import SectionNumber
from Handlers import Term
from Handlers import TextbookSelection

sessionConfig = {}
sessionConfig['webapp2_extras.sessions'] = {
    'secret_key': 'no-one-will-guess-kwsfs-secret-key',
}

app = webapp2.WSGIApplication([
    ('/', Login.LoginHandler),
    ('/manage.html', Management.ManagementHandler),
    ('/policyLib.html', CoursePolicy.PolicyLibHandler),
    ('/textbookLib.html', TextbookSelection.TextbookLibHandler),
    ('/syllabusStepTerm.html', Term.TermHandler),
    ('/syllabusStepDepartment.html', Department.DepartmentHandler),
    ('/syllabusStepCourseNumber.html', CourseNumber.CourseNumberHandler),
    ('/syllabusStepSectionNumber.html', SectionNumber.SectionNumberHandler),
    ('/syllabusStepTextbookSelection.html', TextbookSelection.TextbookSelectionHandler),
    ('/syllabusStepAssessment.html', Assessment.AssessmentHandler),
    ('/syllabusStepGradeScale.html', GradeScale.GradeScaleHandler),
    ('/syllabusStepPoliciesEditor.html', CoursePolicy.CoursePolicyEditHandler),
    ('/syllabusStepCalendar.html', Calendar.CalendarHandler),
    ('/deleteCalendarEntry', Calendar.DeleteCalendarEntryHandler),
    ('/updateCalendarEntries', Calendar.UpdateCalendarEntriesHandler),
    ('/addDate', Calendar.AddDateHandler),
    ('/syllabusStepCompletion.html', Completion.CompletionHandler),
    ('/syllabusStepInstructor.html', InstructorStep.InstructorStepHandler),
    ('/delinkPolicy', CoursePolicy.DelinkPolicyHandler),
    ('/deletePolicy', CoursePolicy.DeletePolicyHandler),
    ('/editPolicy', CoursePolicy.EditPolicyHandler),
    ('/linkPolicy', CoursePolicy.LinkPolicyHandler),
    ('/schedule', Schedule.ScheduleHandler),
    ('/copyCalendar', Calendar.CopyCalendarHandler),
    ('/scrape', Scraper.ScraperHandler),
    webapp2.Route(r'/<username>/<termyear>/<schoolclass>/<section>/<syllabusID>',
                  handler=CompletedSyllabus.CompletedSyllabusHandler)
], debug=True, config=sessionConfig)
