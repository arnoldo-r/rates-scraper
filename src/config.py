from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    bcv_url: str
    timezone: str
    date_selector: str
    usd_selector: str
    eur_selector: str

def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing environment variable: {name}")
    return value

def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        bcv_url=_required("BCV_URL"),
        timezone=_required("LOCAL_TIMEZONE"),
        date_selector=_required("BCV_DATE_SELECTOR"),
        usd_selector=_required("BCV_USD_SELECTOR"),
        eur_selector=_required("BCV_EUR_SELECTOR"),
    )
