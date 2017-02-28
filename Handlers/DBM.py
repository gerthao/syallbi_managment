from google.appengine.ext import ndb

def UserKey(userName):
    return ndb.Key(userName, "cafe")

def PolicyKey(policyHead):
    return ndb.Key(policyHead, "policy header")

def SyllabusKey(syllabusName):
    return ndb.Key(syllabusName, "syllabus name")

def GradeKey(syllabusName, gradeName):
    return ndb.Key(syllabusName, gradeName)

def AssessmentKey(syllabusName, assessmentName):
    return ndb.Key(syllabusName, assessmentName)

def InstructorKey(syllabusName, instructorName):
    return ndb.Key(syllabusName, instructorName)

def TextbookKey(syllabusName):
    return ndb.Key(syllabusName, "stuff")

def CalendarKey(calendarName):
    return ndb.Key(calendarName, "calendar name")

class Textbook(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    author = ndb.StringProperty(indexed=True)
    ISBN = ndb.StringProperty(indexed=True)
    syllabusName = ndb.StringProperty(indexed=True)
    publisher = ndb.StringProperty(indexed=True)
    edition = ndb.StringProperty(indexed=True)

class Instructor(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    phone = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    officeLocation = ndb.StringProperty(indexed=True)
    officeHours = ndb.StringProperty(indexed=True)
    syllabusName = ndb.StringProperty(indexed=True)

class Term(ndb.Model):
    """Main model for a term"""
    year = ndb.IntegerProperty(indexed=True)
    term = ndb.StringProperty(indexed=True)


class User(ndb.Model):
    """Main model for representing a user."""
    username = ndb.StringProperty(indexed=True)
    password = ndb.StringProperty(indexed=False)


class Policy(ndb.Model):
    """Main model for representing a policy."""
    head = ndb.StringProperty(indexed=True)
    body = ndb.StringProperty(indexed=False)
    updatedOn = ndb.DateProperty(auto_now=True)


class Assessment(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    percent = ndb.StringProperty(indexed=True)
    description = ndb.StringProperty(indexed=True)
    syllabusName = ndb.StringProperty(indexed=True)

class Grade(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    percentRange = ndb.StringProperty(indexed=True)
    syllabusName = ndb.StringProperty(indexed=True)

class Course(ndb.Model):
    department = ndb.StringProperty(indexed=True)
    course_number = ndb.IntegerProperty(indexed=True)
    section_number = ndb.IntegerProperty(indexed=True)

class Syllabus(ndb.Model):
    """Main model for representing a syllabus (incomplete)."""
    name = ndb.StringProperty(indexed=True)
    term = ndb.StructuredProperty(Term, repeated=False)
    course = ndb.StructuredProperty(Course, repeated=False)
    policies = ndb.KeyProperty(repeated=True)
    assessments = ndb.StructuredProperty(Assessment, repeated=True)
    gradeScale = ndb.StructuredProperty(Grade, repeated=True)
    active = ndb.BooleanProperty(indexed=True)
    Instructors = ndb.StructuredProperty(Instructor, repeated=True)
    textbooks = ndb.StructuredProperty(Textbook, repeated=True)
    calendar = ndb.KeyProperty(repeated=False)
    owner = ndb.StringProperty(indexed=True)

    def getLink(self):
        result = "/"+str(self.owner)+"/"+str(self.term.term)+str(self.term.year)+"/"
        result += str(self.course.department)+str(self.course.course_number)+"/"+str(self.course.section_number)
        result += "/"+str(self.name)
        return result

    def toString(self):
        return str(self.course.department) + str(self.course.course_number) + "-S" + str(self.course.section_number)

class DateEvent(ndb.Model):
    date = ndb.DateProperty(indexed=False)
    event = ndb.StringProperty(indexed=False)
    homework = ndb.StringProperty(indexed=False)

class Calendar(ndb.Model):
    entries = ndb.StructuredProperty(DateEvent, repeated=True)
    daysActive = ndb.IntegerProperty(repeated=True)
    name = ndb.StringProperty(indexed=True)
