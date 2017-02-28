import Base
import DBM

class CourseNumberHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template_values = {'progress': 2}
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepCourseNumber.html')
        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return
        c_num = self.request.get("course-number")
        c_num = int(c_num)
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]

        syllabus.course.course_number = c_num

        syllabus.put()

        self.redirect('syllabusStepSectionNumber.html')

