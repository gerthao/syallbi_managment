from datetime import date, timedelta
import Base
import DBM


class CalendarHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template_values = {'progress': 7, 'weekdayPrinter': weekdayPrinter}
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepCalendar.html')

        calendar = getCurrentCalendar(self.session.get("currentSyllabus"))

        template_values['date_events'] = calendar.entries

        self.response.write(template.render(template_values))


class DeleteCalendarEntryHandler(Base.BaseHandler):
    def post(self):
        if not self.check_login(): return

        toRemove = self.request.get("toRemove")
        calendar = getCurrentCalendar(self.session.get("currentSyllabus"))

        # find first entry with the date, remove it and continue
        for i in calendar.entries:
            if str(i.date) == toRemove:
                calendar.entries.remove(i)
                break

        calendar.put()

        self.redirect("/syllabusStepCalendar.html")


class UpdateCalendarEntriesHandler(Base.BaseHandler):
    def post(self):
        if not self.check_login(): return

        calendar = getCurrentCalendar(self.session.get("currentSyllabus"))
        newHW = self.request.get_all("homework")
        newEvents = self.request.get_all("event")

        # update all calendar entry fields
        x = 0
        for i in calendar.entries:
            i.homework = newHW[x]
            i.event = newEvents[x]
            x += 1

        calendar.put()

        self.redirect("/syllabusStepCalendar.html")


class AddDateHandler(Base.BaseHandler):
    def post(self):
        newYear = int(self.request.get("year"))
        newMonth = int(self.request.get("month"))
        newDay = int(self.request.get("day"))

        addDateToCalendar(self.session.get("currentSyllabus"), date(newYear, newMonth, newDay))

        self.redirect("/syllabusStepCalendar.html")


class CopyCalendarHandler(Base.BaseHandler):
    def get(self):
        template = Base.JINJA_ENVIRONMENT.get_template('syllabusStepCopyCalendar.html')
        template_values = {'progress': 7, 'calendars': []}

        allSyllabus = DBM.Syllabus.query().fetch()
        currentSyllabus = self.session.get("currentSyllabus")

        for i in allSyllabus:
            if i.name != currentSyllabus:
                template_values['calendars'].append(i.name)

        self.response.write(template.render(template_values))

    def post(self):
        source = self.request.get('source')
        destination = self.session.get("currentSyllabus")

        copyCalendar(source, destination)

        self.redirect("/syllabusStepCalendar.html")


def addDateToCalendar(name, newDate):
    calendar = DBM.Calendar.query(ancestor=DBM.CalendarKey(name)).fetch(1)[0]

    newDateEntry = DBM.DateEvent(date=newDate, homework="", event="")

    inserted = False

    # insert data at proper date location
    for i in range(0, len(calendar.entries)):
        if calendar.entries[i].date > newDate:
            calendar.entries.insert(i, newDateEntry)
            inserted = True
            break

    # insert at end if we couldn't find a place at the beginning or middle
    if not inserted:
        calendar.entries.append(newDateEntry)

    calendar.put()


# tries to get the current calendar being edited
# if there is no current calendar, it returns a new calendar linked to the current syllabus
def getCurrentCalendar(name):
    calendar = DBM.Calendar.query(ancestor=DBM.CalendarKey(name)).fetch(1)

    if len(calendar) > 0:
        return calendar[0]
    else:
        newCalendarKey = DBM.CalendarKey(name)
        calendar = DBM.Calendar(parent=newCalendarKey, name=name, entries=[])

        # TODO: remove hard coded values when parser is done, replace with error handling
        startDate = date(2015, 8, 1)
        endDate = date(2016, 2, 1)
        daysOfWeek = [0, 2, 4]
        calendar.entries = generateEntryRange(startDate, endDate, daysOfWeek)

        calendar.put()
        syllabus = DBM.Syllabus.query(ancestor=DBM.SyllabusKey(name)).fetch(1)[0]
        syllabus.calendar = calendar.key
        syllabus.put()
        return calendar


# returns an array of DateEvents for the given date range on the proper days of the week
def generateEntryRange(startDate, endDate, daysOfWeek):
    result = []

    while startDate <= endDate:
        if startDate.weekday() in daysOfWeek:
            result.append(DBM.DateEvent(date=startDate, event="", homework=""))
        startDate += timedelta(days=1)

    return result


# copies the calendar contents from syllabusA to syllabusB using indexes (not dates!)
# syllabusB must already be populated with empty date entries
# excess dates are chopped off
def copyCalendar(syllabusA, syllabusB):
    calendarA = DBM.Calendar.query(ancestor=DBM.CalendarKey(syllabusA)).fetch(1)[0]
    calendarB = DBM.Calendar.query(ancestor=DBM.CalendarKey(syllabusB)).fetch(1)[0]

    index = 0
    for entry in calendarA.entries:
        calendarB.entries[index].homework = entry.homework
        calendarB.entries[index].event = entry.event
        index += 1
        if index >= len(calendarB.entries) - 1:
            break

    calendarB.put()

    return


# Returns an array from startDate to endDate with the class names that occur on each days in sub-arrays
def getClasssesAndDays(startDate, endDate):
    results = []
    oneDay = timedelta(days=1)

    # initialize results to proper size
    dateIterator = startDate
    while dateIterator <= endDate:
        results.append([])
        dateIterator += oneDay

    syllabus = DBM.Syllabus.query(DBM.Syllabus.active == True).fetch()

    for i in syllabus:
        calendar = i.calendar.get()
        calendarStart = calendar.entries[0].date
        calendarEnd = calendar.entries[len(calendar.entries) - 1].date

        # if overlap occurs, then we perform a full analysis and insertion
        if startDate <= calendarEnd and endDate >= calendarStart:
            # append to all relevant dates

            calendarDates = []
            for date in calendar.entries:
                calendarDates.append(date.date)

            dateIterator = startDate
            index = 0
            while dateIterator <= endDate:
                if dateIterator in calendarDates:
                    results[index].append(i)
                index += 1
                dateIterator += oneDay

    return results


weekdayPrinter = ['Monday',
                  'Tuesday',
                  'Wednesday',
                  'Thursday',
                  'Friday',
                  'Saturday',
                  'Sunday']
