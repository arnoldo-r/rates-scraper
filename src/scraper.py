from __future__ import annotations

import datetime
from decimal import InvalidOperation

import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config import Settings
from data_manager import Rate, _rate_to_cents

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def _text(soup: BeautifulSoup, selector: str) -> str | None:
    node = soup.select_one(selector)
    if node is None:
        return None
    text = node.get_text(strip=True).replace(",", ".")
    return text or None

def _content(soup: BeautifulSoup, selector: str) -> str | None:
    node = soup.select_one(selector)
    if node is None:
        return None
    value = node.attrs.get("content")
    if not isinstance(value, str) or not value:
        return None
    return value

def scrape_bcv_data(settings: Settings) -> Rate | None:
    try:
        response = requests.get(
            settings.bcv_url,
            timeout=10,
            verify=False,
            allow_redirects=False,
        )
        if 300 <= response.status_code < 400:
            print("Error fetching BCV data: Redirect")
            return None
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        date_text = _content(soup, settings.date_selector)
        usd_text = _text(soup, settings.usd_selector)
        eur_text = _text(soup, settings.eur_selector)
        if date_text is None or usd_text is None or eur_text is None:
            print("Error processing BCV data: MissingValue")
            return None
        return Rate(
            datetime.datetime.fromisoformat(date_text).date(),
            _rate_to_cents(usd_text),
            _rate_to_cents(eur_text),
        )
    except requests.RequestException as exc:
        print(f"Error fetching BCV data: {type(exc).__name__}")
        return None
    except (ValueError, InvalidOperation, ArithmeticError) as exc:
        print(f"Error processing BCV data: {type(exc).__name__}")
        return None
