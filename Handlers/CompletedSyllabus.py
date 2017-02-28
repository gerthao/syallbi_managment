import re

import Base
import CoursePolicy
import DBM


class CompletedSyllabusHandler(Base.BaseHandler):
    def get(self, username, termyear, schoolclass, section, syllabusID):
        template_values = {}
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusViewer.html')

        # TODO: Needs more error handling
        errors = ""

        year = int(re.search(r'\d+', termyear).group())
        errors += "year: " + str(year)
        term = ''.join([i for i in termyear if not i.isdigit()])
        errors += ", term: " + term

        classNumber = int(re.search(r'\d+', schoolclass).group())
        errors += ", class number: " + str(classNumber)
        school = ''.join([i for i in schoolclass if not i.isdigit()])
        errors += ", school: " + school

        sectionNumber = int(re.search(r'\d+', section).group())
        errors += ", section number: " + str(sectionNumber)

        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(syllabusID)).fetch(1)

        if len(syllabus) > 0:
            syllabus = syllabus[0]

        # TODO: refactor this into a smaller statement
        if (syllabus.active and syllabus.course.department == school and syllabus.owner == username and
                    syllabus.course.course_number == classNumber and
                    syllabus.term.year == year and syllabus.term.term == term and
                    syllabus.course.section_number == sectionNumber):
            template_values['syllabus'] = syllabus
            template_values['policies'] = CoursePolicy.getPoliciesBySyllabus(syllabus.name)
            template_values['calendar'] = syllabus.calendar.get()
            self.response.write(template.render(template_values))
        else:
            self.response.write("The following information is not a valid active syllabus: <br>" + errors)
