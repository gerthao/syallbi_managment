import Base
import DBM

class GradeScaleHandler(Base.BaseHandler):
    template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepGradeScale.html')


    def get(self):
        if not self.check_login(): return
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
        syllabusName = syllabus.name
        scale = syllabus.gradeScale

        template_values = {'progress': 6, 'grades': scale} #TODO gradescale table information after progress
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepGradeScale.html')
        self.response.write(self.template.render(template_values))

    def post(self):
            if not self.check_login(): return

            syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
            scale = syllabus.gradeScale

            gradeObj = self.request.get("delete")
            if(len(gradeObj) != 0):
                index = 0
                deleteName = self.request.get("delete_name")
                deleteQuantity = self.request.get("delete_quantity")
                for g in scale:
                    if (deleteName == g.name and deleteQuantity == g.percentRange):
                        break;
                    index = index + 1;

                del scale[index]
                syllabus.put()
                self.get()
                return
            gradeName = self.request.get("gradeName")
            newGrade = DBM.Grade(parent=DBM.GradeKey(syllabus.name, gradeName),
                            name=gradeName,
                            percentRange=self.request.get("gradePercentageRange"),
                            syllabusName=syllabus.name)

            syllabus.gradeScale.append(newGrade)
            syllabus.put()
            self.get()