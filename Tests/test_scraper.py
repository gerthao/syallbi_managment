from Scraper import Scraper
import unittest

def test_scrape_main_schedule_page_return_list_of_terms(self):
    expected = [('Spring', 2016), ('UWinteriM', 2016), ('Fall', 2015), ('Summer', 2015)]
    myScraper = Scraper()
    actual = myScraper.scrape_schedule_main_page()
    self.assertEqual(expected, actual)

test_scrape_main_schedule_page_return_list_of_terms()

if __name__ == '__main__':
    unittest.main()
