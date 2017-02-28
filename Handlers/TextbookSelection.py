import Base
import DBM
from datetime import date

class TextbookSelectionHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        syllabus = \
            DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepTextbookSelection.html')
        self.response.write(template.render(self.getTemplate(syllabus)))

    def getTemplate(self, syllabus):
        syllabus_textbooks = syllabus.textbooks
        course_section = str(syllabus.course.section_number)
        if len(course_section) == 1:
            course_section = "00"+course_section
        elif len(course_section) == 2:
            course_section = "0"+course_section
        template_values = {'progress': 4,
                           'l1': syllabus_textbooks,
                           'length': len(syllabus_textbooks),
                           'course': syllabus.course,
                           'section': course_section}
        return template_values

    def post(self):
        if not self.check_login(): return
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]
        syllabus_textbooks = syllabus.textbooks

        removeTextbook = self.request.get("delete")
        if(len(removeTextbook) != 0):
            index = 0
            deleteTitle = self.request.get("delete_title")
            deleteAuthor = self.request.get("delete_author")
            #deleteISBN = self.request.get("delete_ISBN")
            #deleteDate = self.request.get("delete_date")
            for textbook in syllabus_textbooks:
                if (deleteTitle == textbook.title and deleteAuthor == textbook.author):
                    break
                index = index + 1

            del syllabus_textbooks[index]
            syllabus.put()
            self.get()
            return

        new_textbook = DBM.Textbook(parent=DBM.TextbookKey(self.session.get("currentSyllabus")),
                                    title=self.request.get("title"),
                                    author=self.request.get("author"),
                                    ISBN=self.request.get("ISBN"),
                                    publisher=self.request.get("publisher"),
                                    edition=self.request.get("edition"))
        syllabus.textbooks.append(new_textbook)
        syllabus.put()
        new_textbook.put()
        self.get()


class TextbookLibHandler(Base.BaseHandler):
    def get_syllabus(self):
        return DBM.Textbook.query(ancestor=DBM.TextbookKey(self.session.get('currentSyllabus'))).fetch(1)[0]

    def get(self):
        if not self.check_login(): return

        syllabus = \
            DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]

        template = Base.JINJA_ENVIRONMENT.get_template('textbookLib.html')
        self.response.write(template.render(self.get_template_value(syllabus)))

    def get_template_value(self, syllabus):
        if syllabus is None:
            template_values = {'l1': None, 'length': 0}
        else:
            textbooks = syllabus.textbooks
            template_values = {'l1': textbooks, 'length': len(textbooks)}
        return template_values

    def post(self):
        if not self.check_login(): return

        syllabus = \
            DBM.Syllabus.query(ancestor=DBM.SyllabusKey(self.session.get('currentSyllabus'))).fetch(1)[0]

        syllabusName = syllabus.name
        newTextbook = DBM.Textbook(parent=DBM.TextbookKey(syllabus.name),
                                        title=self.request.get("title"),
                                        author=self.request.get("author"),
                                        ISBN=self.request.get("ISBN"))
        syllabus.textbooks.append(newTextbook)
        syllabus.put()
        #newTextbook.put()
        self.get()
