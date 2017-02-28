import Base
import DBM

class SectionNumberHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template_values = {'progress': 2}
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepSectionNumber.html')
        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return
        s_num = self.request.get("section-number")

        s_num = int(s_num)
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]

        syllabus.course.section_number = s_num

        syllabus.put()

        self.redirect('syllabusStepInstructor.html')
