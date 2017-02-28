import Base
import DBM

class TermHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template_values = {'progress': 1}
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepTerm.html')
        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return
        term = self.request.get('term')
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
        year = self.request.get('year')
        year = int(year)
        syllabus.term = DBM.Term(term=term, year=year)

        syllabus.put()

        self.redirect('syllabusStepDepartment.html')