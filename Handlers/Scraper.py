import Base
from ScraperModule import ScraperStart

class ScraperHandler(Base.BaseHandler):

    def get(self):
        my_scraper = ScraperStart.ScraperStart()
        my_scraper.scrape_main_schedule_page()
        self.response.write("Scraping Complete")
