from bs4 import BeautifulSoup
from urllib import urlopen
# from Handlers import DBM
from datetime import date
# import TermDBM
import ScraperStart

class GScraper:
    department_url = ""
    database = ""

    def scrape(self, url, db_object):
        html = urlopen(url)
        soup_object = BeautifulSoup(html, "html.parser")
        tables = soup_object.findAll("table")
        for table in tables:
            spans = table.findAll("span", {"class": "subhead"})
            for span in spans:
                course_info = span.renderContents().strip()
                info_2 = course_info.split("-")
                info_3 = info_2.split(":")
                course_number = info_3[0]
                #course = TermDBM.Class(class_number=course_number)

                #     new_department = TermDBM.Department(department_name=department_name)
                # new_department.put()
                #
                # term_db_object.department.append(new_department.key)
                # term_db_object.put()

                course.put()

                tr_tags = table.findAll("tr", {"class": "body copy"})
                for tr in tr_tags:
                    # calendar = DBM.Calendar()
                    # instructor = DBM.Instructor()
                    info_list = tr.findChildren()

                    course.section_number = int(info_list[3].renderContents().strip())

                    lecture_days = self.days_to_ints(info_list[6].renderContents().strip())

                    dates = info_list[7].renderContents().strip().split("-")
                    star = dates[0]
                    en = dates[1]
                    start = date(2016, int(star.split("/")[0], int(star.split("/")(1))))
                    end = date(2016, int(en.split("/")[0], int(en.split("/")(1))))
                    calendar.daysActive = self.delta_days(start, end)

                    instructor.name = info_list[8].renderContents().strip()
        return self

    def days_to_ints(self, days):
        week = [0, 0, 0, 0, 0]
        if days.find("M") == 1:
            week[0] = 1
        if days.find("T") == 1:
            week[1] = 1
        if days.find("W") == 1:
            week[2] = 1
        if days.find("R") == 1:
            week[3] = 1
        if days.find("F") == 1:
            week[4] = 1
        return week

    def delta_days(self, start, end):
        delta = end - start
        return delta.days


def main():
    html = urlopen("UWM Online Schedule of Classes.html").read()
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.findAll("table")
    for table in tables:
        spans = table.findAll("span", {"class": "subhead"})
        for span in spans:
           print span.renderContents().strip()
           tr_tags = table.findAll("tr", {"class": "body copy"})
           for tr in tr_tags:
               i = 0
               for tr_children in tr.findChildren():
                   if i == 3 or i == 5 or i == 6 or i == 7 or i == 8 or i == 9:
                       print "[%s]: %s" % (i, tr_children.renderContents().strip())
                   i += 1
               print

if __name__=="__main__": main()

