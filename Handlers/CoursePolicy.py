import Base
import DBM


class CoursePolicyEditHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return

        template_values = {'progress': 6}
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepPoliciesEditor.html')

        template_values['importedPolicies'] = getPoliciesBySyllabus(self.session.get("currentSyllabus"))

        allPolicies = DBM.Policy.query().fetch()

        for val in template_values['importedPolicies']:
            for policy in allPolicies:
                if val.head == policy.head:
                    allPolicies.remove(policy)

        template_values['otherPolicies'] = allPolicies

        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return

        newPolicyHeader = ""
        newPolicyBody = ""

        # generic exception for now
        try:
            newPolicyHeader = self.request.get('policyHeader')
            newPolicyBody = self.request.get('policyBody')
        except:
            self.redirect('/syllabusStepPoliciesEditor.html')
            return

        savePolicyToSyllabus(newPolicyHeader, newPolicyBody, self.session.get("currentSyllabus"))

        self.redirect('/syllabusStepPoliciesEditor.html')


class LinkPolicyHandler(Base.BaseHandler):
    def post(self):
        if not self.check_login(): return

        imports = []

        try:
            imports = self.request.get_all("selectedImports")
        except:
            self.redirect("/syllabusStepPoliciesEditor.html")
            return

        for i in imports:
            linkPolicyToSyllabus(i, self.session.get("currentSyllabus"))

        self.redirect("/syllabusStepPoliciesEditor.html")


class DelinkPolicyHandler(Base.BaseHandler):
    def post(self):
        if not self.check_login(): return
        delinkPolicyFromSyllabus(self.request.get('policyHead'), self.session.get('currentSyllabus'))
        self.redirect(self.request.get('source'))


class DeletePolicyHandler(Base.BaseHandler):
    def post(self):
        if not self.check_login(): return
        deletePolicy(self.request.get('policyHead'))
        self.redirect(self.request.get('source'))


class PolicyLibHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template_values = {'editMode': False}
        template = Base.JINJA_ENVIRONMENT.get_template('policyLib.html')
        template_values['policies'] = DBM.Policy.query().fetch()
        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return

        newPolicyHeader = ""
        newPolicyBody = ""

        try:
            newPolicyHeader = self.request.get("newPolicyHeader")
            newPolicyBody = self.request.get("newPolicyBody")
        except:
            self.redirect('/policyLib.html')
            return

        savePolicy(newPolicyHeader, newPolicyBody)

        self.redirect('/policyLib.html')


class EditPolicyHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template_values = {'editMode': True}
        oldPolicyHeader = self.request.get("oldPolicyHead")
        template_values['oldPolicyHeader'] = oldPolicyHeader
        policy = DBM.Policy.query(ancestor=DBM.PolicyKey(oldPolicyHeader)).fetch(1)[0]
        template_values['oldPolicyBody'] = policy.body
        template = Base.JINJA_ENVIRONMENT.get_template('policyLib.html')
        self.response.write(template.render(template_values))

    def post(self):
        if not self.check_login(): return
        editPolicy(self.request.get("oldPolicyHead"), self.request.get("newPolicyBody"))
        self.redirect('/policyLib.html')


def getPoliciesBySyllabus(syllabus):
    policiesFound = []
    policiesQueried = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(syllabus)).fetch(1)[0].policies
    for i in policiesQueried:
        policyLookup = DBM.Policy.query(ancestor=i).fetch(1)
        # avoids displaying deleted keys TODO: find a long term solution to remove keys when deleting policies
        if len(policyLookup) != 0:
            policiesFound.append(policyLookup[0])

    return policiesFound


def savePolicyToSyllabus(newPolicyHeader, newPolicyBody, syllabus):
    newPolicyKey = savePolicy(newPolicyHeader, newPolicyBody)

    if newPolicyKey != False:
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(syllabus)).fetch(1)[0]
        syllabus.policies.append(newPolicyKey)
        syllabus.put()
    else:
        return False


def savePolicy(newPolicyHeader, newPolicyBody):
    # no errors for now
    if newPolicyHeader == "" or newPolicyBody == "":
        return False

    if len(DBM.Policy.query(ancestor=DBM.PolicyKey(newPolicyHeader)).fetch()) > 0:
        return False

    newPolicyKey = DBM.PolicyKey(newPolicyHeader)
    newPolicy = DBM.Policy(parent=newPolicyKey, head=newPolicyHeader, body=newPolicyBody)
    newPolicy.put()
    return newPolicyKey


def delinkPolicyFromSyllabus(toDelink, syllabus):
    syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(syllabus)).fetch(1)[0]
    syllabus.policies.remove(DBM.PolicyKey(toDelink))
    syllabus.put()


def linkPolicyToSyllabus(policyHeader, syllabus):
    newPolicyKey = DBM.PolicyKey(policyHeader)

    if newPolicyKey != False:
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(syllabus)).fetch(1)[0]
        syllabus.policies.append(newPolicyKey)
        syllabus.put()
    else:
        return False


def deletePolicy(toDelete):
    deleteThis = DBM.Policy.query(ancestor=DBM.PolicyKey(toDelete)).fetch(1)
    if len(deleteThis) > 0:
        deleteThis[0].key.delete()


def editPolicy(oldHeader, newBody):
    policy = DBM.Policy.query(ancestor=DBM.PolicyKey(oldHeader)).fetch(1)

    if len(policy) == 0 or newBody == "":
        return False

    policy = policy[0]
    policy.body = newBody
    policy.put()
