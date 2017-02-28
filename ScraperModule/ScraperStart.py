import urllib
import re
import TermDBM
from bs4 import BeautifulSoup
import GScraper

class ScraperStart:

    def __init__(self):
        self.terms = []
        self.term_links = []

    def scrape_main_schedule_page(self):
        site = urllib.urlopen("http://www4.uwm.edu/schedule/")

        soup = BeautifulSoup(site)
        filtered_html = soup.find_all("a", {"class": "term_link" })
        for url in filtered_html:
            url = url['href']

        term_link_beginning = "http://www4.uwm.edu/schedule/"


        for link in filtered_html:

            self.term_links.append(term_link_beginning + link)
            full_term = re.findall("term_descr=(.*)&term_status", link)
            current_term = (tuple(full_term[0].split(" ")))
            term = (current_term[0], int(current_term[1]))

            self.add_new_term(term)

            self.term_scraper(term_link_beginning + link, new_term)
            print term

        return


    def term_scraper(self, link, term_db_object):
        site = urllib.urlopen(link)
        soup = BeautifulSoup(site)
        body = soup.body
        div_one = body.contents[2]
        div_two = div_one.contents[0]
        div_three = div_two.contents[0]
        div_four = div_three.contents[1]
        div_five = div_four.contents[0]
        table_one = div_five.contents[8]
        tbody_one = table_one.contents[1]
        tr_one = tbody_one.contents[5]
        links = tr_one.find_all('a')

        for link in links:
            url = link['href']
            full_url = "http://www4.uwm.edu/schedule/" + url
            department_name = link.text
            new_department = TermDBM.Department(department_name=department_name)
            new_department.put()

            # term_db_object.department.append(new_department.key)
            # term_db_object.put()

            # scraper = GScraper.GScraper()
            # scraper.scrape(full_url, new_department)


    def add_new_term(self, term):
        new_term = TermDBM.Term(year=term[1], semester=term[0])
        new_term.put()
        return

    def scrape_department(self, link):
        print link
        return

#
# myScraper = ScraperStart()
# #myScraper.scrape_main_schedule_page()
# #myScraper.scrape_departments_list_page("http://www4.uwm.edu/schedule/index.cfm?a1=browse&strm=2162&term_descr=Spring%202016&term_status=L", "abc")
# myScraper.term_scraper("http://www4.uwm.edu/schedule/index.cfm?a1=browse&strm=2162&term_descr=Spring%202016&term_status=L")