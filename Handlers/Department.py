import Base
import DBM


class DepartmentHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template_values = {'progress': 2}
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepDepartment.html')
        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return
        new_department = self.request.get("department")
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
        course = DBM.Course(department=new_department)

        syllabus.course = course
        # course.put()
        syllabus.put()

        self.redirect('/syllabusStepCourseNumber.html')
