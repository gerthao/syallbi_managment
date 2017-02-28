import Base
import DBM


class AssessmentHandler(Base.BaseHandler):
    template_values = {'progress': 5}
    template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepAssessment.html')
    editIndex = -1

    def get(self):
        if not self.check_login(): return
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
        syllabusName = syllabus.name
        assessments = syllabus.assessments
        self.template_values = {'progress': 5,
                                'l1': assessments,
                                'l1length' : len(assessments),
                                'editIndex' : self.editIndex}
        self.response.write(self.template.render(self.template_values))
        self.editIndex = -1

    def post(self):
        if not self.check_login(): return
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]

        saveEdit = self.request.get("saveEdit")
        if(len(saveEdit) != 0):
            aIndex = int(saveEdit)
            editAssessment = syllabus.assessments[aIndex]
            editAssessment.name = self.request.get("assessmentName")
            editAssessment.percent = self.request.get("assessmentPercent")
            editAssessment.description = self.request.get("assessmentDescription")
            syllabus.put()
            self.get()
            return

        shallWeEdit = self.request.get("edit")
        if(len(shallWeEdit) != 0):
            self.editIndex = int(shallWeEdit)
            self.get()
            return

        indexRemove = self.request.get("delete")
        if(len(indexRemove) != 0):
            indexRemove = int(indexRemove)
            assessmentRemove = syllabus.assessments[indexRemove]
            del syllabus.assessments[indexRemove]
            syllabus.put()
            self.get()
            return
        assessmentName = self.request.get("assessmentName")
        newAssessment = DBM.Assessment(parent=DBM.AssessmentKey(syllabus.name, assessmentName),
                                       name=assessmentName,
                                       percent=self.request.get("assessmentPercent"),
                                       description=self.request.get("assessmentDescription"),
                                       syllabusName=syllabus.name)
        syllabus.assessments.append(newAssessment)
        syllabus.put()

        self.get()
