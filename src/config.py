import os
import pytz
from dotenv import load_dotenv
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests

# Suppress InsecureRequestWarning from urllib3
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

# Get the scraping URL from environment variables
BCV_URL = os.getenv("BCV_URL")
if not BCV_URL:
    print("Error: Scraping URL not configured in .env")
    exit(1)

# Get the local timezone string from environment variables
TIMEZONE_STR = os.getenv("LOCAL_TIMEZONE")
if not TIMEZONE_STR:
    print("Error: Local timezone not configured in .env")
    exit(1)

# Define the local timezone
LOCAL_TZ = pytz.timezone(TIMEZONE_STR)

# Get CSS selectors from environment variables
BCV_DATE_SELECTOR = os.getenv("BCV_DATE_SELECTOR")
BCV_USD_SELECTOR = os.getenv("BCV_USD_SELECTOR")
BCV_EUR_SELECTOR = os.getenv("BCV_EUR_SELECTOR")

# Basic validation for selectors
if not all([BCV_DATE_SELECTOR, BCV_USD_SELECTOR, BCV_EUR_SELECTOR]):
    print("Error: CSS selectors are not configured in .env")
    exit(1)