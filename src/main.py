from config import load_settings
from data_manager import update_rate_files
from scraper import scrape_bcv_data

if __name__ == "__main__":
    settings = load_settings()
    scraped = scrape_bcv_data(settings)
    if scraped:
        update_rate_files(scraped, settings.timezone)
    else:
        print("Could not retrieve data. Rate files were left unchanged.")
