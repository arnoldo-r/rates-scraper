from __future__ import annotations

import datetime
import json
import os
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class Rate:
    date: datetime.date
    usd: int
    eur: int

def _rate_to_cents(raw_value: str) -> int:
    quantized = Decimal(raw_value.strip().replace(",", ".")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return int(quantized * 100)

def applicable_rate(saved: Rate | None, scraped: Rate, today: datetime.date) -> Rate | None:
    if scraped.date < today:
        return saved
    if scraped.date == today or saved is None or saved.date < today:
        return scraped
    return saved

def _data_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "data")

def _current_path() -> str:
    return os.path.join(_data_dir(), "current.json")

def _next_path() -> str:
    return os.path.join(_data_dir(), "next.json")

def _load_rate(path: str) -> Rate | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError:
        print(f"Warning: {os.path.basename(path)} is corrupt or empty.")
        return None
    if not isinstance(payload, dict):
        print(f"Warning: {os.path.basename(path)} is corrupt or empty.")
        return None
    try:
        usd = payload["usd"]
        eur = payload["eur"]
        if isinstance(usd, bool) or isinstance(eur, bool) or not isinstance(usd, int) or not isinstance(eur, int):
            raise TypeError
        return Rate(datetime.date.fromisoformat(payload["date"]), usd, eur)
    except (KeyError, TypeError, ValueError):
        print(f"Warning: {os.path.basename(path)} is corrupt or empty.")
        return None

def _write_rate(path: str, rate: Rate) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"date": rate.date.isoformat(), "usd": rate.usd, "eur": rate.eur}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))

def _remove_if_exists(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)
        print(f"Removed {path}")

def update_rate_files(scraped: Rate, timezone_name: str) -> None:
    today = datetime.datetime.now(ZoneInfo(timezone_name)).date()
    current_path = _current_path()
    next_path = _next_path()

    saved = _load_rate(current_path)
    chosen = applicable_rate(saved, scraped, today)
    if chosen is not None and chosen != saved:
        _write_rate(current_path, chosen)
        print(f"JSON file updated at {current_path}")
    else:
        print(f"JSON file left unchanged at {current_path}")

    if scraped.date > today:
        saved_next = _load_rate(next_path)
        if scraped != saved_next:
            _write_rate(next_path, scraped)
            print(f"JSON file updated at {next_path}")
        else:
            print(f"JSON file left unchanged at {next_path}")
    else:
        _remove_if_exists(next_path)
