import Base
import DBM

class InstructorStepHandler(Base.BaseHandler):
    template_values = {'progress': 3}
    template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepInstructor.html')
    editIndex = -1

    def get(self):
        if not self.check_login(): return
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
        syllabusName = syllabus.name
        Instructors = syllabus.Instructors
        self.template_values = {'progress': 3,
                                'l1': Instructors,
                                'l1Length' : len(Instructors),
                                'editIndex' : self.editIndex}
        self.response.write(self.template.render(self.template_values))
        self.editIndex = -1

    def post(self):
        if not self.check_login(): return
        syllabus = \
            DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]

        shallWeEdit = self.request.get("edit")
        if(len(shallWeEdit) != 0):
            self.editIndex = int(shallWeEdit)
            self.get()
            return

        saveEdit = self.request.get("saveEdit")
        if(len(saveEdit) != 0):
            taIndex = int(saveEdit)
            tempInstructor = syllabus.Instructors[taIndex]
            tempInstructor.name = self.request.get("name")
            tempInstructor.phone = self.request.get("phone")
            tempInstructor.email = self.request.get("email")
            tempInstructor.officeLocation = self.request.get("location")
            tempInstructor.officeHours = self.request.get("hours")
            syllabus.put()
            self.get()
            return

        removeIndex = self.request.get("remove")
        if(len(removeIndex) != 0):
            removeIndex = int(removeIndex)
            del syllabus.Instructors[removeIndex]
            syllabus.put()
            self.get()
            return
        InstructorName = self.request.get("name")
        newInstructor = DBM.Instructor(parent=DBM.InstructorKey(syllabus.name, InstructorName),
                                        name=InstructorName,
                                        phone=self.request.get("phone"),
                                        email=self.request.get("email"),
                                        officeLocation=self.request.get("location"),
                                        officeHours=self.request.get("hours"),
                                        syllabusName=syllabus.name)
        syllabus.Instructors.append(newInstructor)
        syllabus.put()
        self.get()
