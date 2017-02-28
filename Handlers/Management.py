import Base
import DBM


class ManagementHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template = Base.JINJA_ENVIRONMENT.get_template('manage.html')
        l1 = list(DBM.Syllabus.query())

        template_values = {'l1': l1,
                           'l1Length': len(l1)}
        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return

        removeIndex = self.request.get("delete")
        if (len(removeIndex) != 0):
            l1 = list(DBM.Syllabus.query())
            index = int(removeIndex)
            syllabusRemove = l1[index]
            syllabusRemove.key.delete()
            self.get()
            return

        newSyllabusName = self.request.get('syllabusName')
        newSyllabus = DBM.Syllabus(parent=DBM.SyllabusKey(newSyllabusName), name=newSyllabusName,
                                   owner=self.session.get("username"), active=False)
        newSyllabus.put()
        self.session['currentSyllabus'] = newSyllabusName
        self.redirect("/syllabusStepTerm.html")
