import datetime

import Base
import Calendar


class ScheduleHandler(Base.BaseHandler):
    def get(self):
        if not self.check_login(): return
        template_values = {'progress': 7, 'active_page': "schedule"}
        template = Base.JINJA_ENVIRONMENT.get_template('schedule.html')

        # TODO: figure out actual date range to calculate
        # get first and last day for calendar generation
        firstDay = datetime.date.today() + datetime.timedelta(days=-2)
        lastDay = firstDay + datetime.timedelta(days=30)

        template_values['schedule'] = Calendar.getClasssesAndDays(firstDay, lastDay)
        template_values['month'] = firstDay.strftime("%B")
        template_values['days'] = []
        template_values['dates'] = []
        template_values['entriesPerRow'] = 7

        # generate days and dates list
        dateIterator = firstDay
        while dateIterator <= lastDay:
            if len(template_values['days']) < 7:
                template_values['days'].append(dateIterator.strftime('%A'))
            template_values['dates'].append(dateIterator.day)
            dateIterator += datetime.timedelta(days=1)

        self.response.write(template.render(template_values))
