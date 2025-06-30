import requests
from bs4 import BeautifulSoup
import datetime
from config import BCV_URL, BCV_DATE_SELECTOR, BCV_USD_SELECTOR, BCV_EUR_SELECTOR

def scrape_bcv_data():
    """Scrapes EUR and USD values and their timestamp from the configured website."""
    try:
        # Keep verify=False to bypass SSL certificate verification
        response = requests.get(BCV_URL, timeout=10, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        usd_value = None
        eur_value = None
        timestamp_str = None

        # Extract timestamp
        date_span = soup.select_one(BCV_DATE_SELECTOR)
        if date_span and 'content' in date_span.attrs:
            timestamp_str = date_span['content']

        # Find USD value
        dolar_div = soup.select_one(BCV_USD_SELECTOR)
        if dolar_div:
            dolar_text = dolar_div.text.strip()
            usd_value = float(dolar_text.replace(',', '.'))

        # Find EUR value
        euro_div = soup.select_one(BCV_EUR_SELECTOR)
        if euro_div:
            euro_text = euro_div.text.strip()
            eur_value = float(euro_text.replace(',', '.'))

        # Parse date string to a date object
        scraped_date = None
        if timestamp_str:
            try:
                dt_object = datetime.datetime.fromisoformat(timestamp_str)
                scraped_date = dt_object.date()
            except ValueError:
                print("Warning: Could not parse timestamp from page.")

        return {
            "scraped_date": scraped_date,
            "usd_bcv": usd_value,
            "eur_bcv": eur_value
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from the configured URL: {e}")
        return None
    except Exception as e:
        print(f"Error processing data from the configured URL: {e}")
        return None