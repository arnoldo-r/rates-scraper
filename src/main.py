import os
from scraper import scrape_bcv_data
from data_manager import update_json_file

if __name__ == "__main__":
    scraped_data = scrape_bcv_data()
    if scraped_data:
        update_json_file(scraped_data)
    else:
        print("Could not retrieve data. JSON file might not have been updated.")