from google.appengine.ext import ndb

class Section(ndb.Model):
    section_number = ndb.IntegerProperty(indexed=True, repeated=False)

class Class(ndb.Model):
    class_number = ndb.IntegerProperty(indexed=True, repeated=False)
    calendar = ndb.KeyProperty(repeated=False)
    instructor = ndb.KeyProperty(repeated=False)
    sections = ndb.KeyProperty(repeated=True)

class Instructor(ndb.Model):
    name = ndb.StringProperty(indexed=True, repeated=False)

class Department(ndb.Model):
    department_name = ndb.StringProperty(indexed=True, repeated=False)
    classes = ndb.KeyProperty(repeated=True)

class Term(ndb.Model):
    year = ndb.IntegerProperty(indexed=True, repeated=False)
    semester = ndb.StringProperty(indexed=True, repeated=False)
    department = ndb.KeyProperty(repeated=True)
