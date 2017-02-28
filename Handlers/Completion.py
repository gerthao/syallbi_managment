import Base
import DBM

class CompletionHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        syllabus = \
            DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]

        policies = []
        for i in syllabus.policies: #stole directly from CoursePolicy.py
            policyLookup = DBM.Policy.query(ancestor=i).fetch(1)
            # avoids displaying deleted keys TODO: find a long term solution to remove keys when deleting policies
            if len(policyLookup) != 0:
                policies.append(policyLookup[0])

        template_values = {'progress': 8,
                           'policies' : policies,
                           'syllabus' : syllabus}
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepCompletion.html')
        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return

        #means the post request is coming from the management page
        syllabusName = self.request.get("edit")
        if(len(syllabusName) > 0):
            self.session['currentSyllabus']=syllabusName
            syllabus = \
                DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
            self.get()
            return()

        #means the post request is coming from the activate/deactive in the completion page
        status = self.request.get("toggleActiveStatus")
        if(len(status) > 0):
            syllabus = \
                DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
            if(status == "True"):
                syllabus.active = True
            if(status == "False"):
                syllabus.active = False
            syllabus.put()
            self.get()
            return()