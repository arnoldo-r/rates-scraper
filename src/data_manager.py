import json
import os
import datetime
from time_utils import get_current_local_date

def _load_or_initialize_json(filepath):
    """
    Loads existing JSON data from the file.
    If the file does not exist, is empty, or corrupt, returns an initial structure.
    """
    initial_data = {"current_rate": None, "next_rate": None}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, dict):
                    # Ensure structure is maintained, even if old file lacks keys
                    initial_data["current_rate"] = existing_data.get("current_rate")
                    initial_data["next_rate"] = existing_data.get("next_rate")
                print("Existing JSON data loaded.")
        except json.JSONDecodeError:
            print("Warning: Existing JSON file is corrupt or empty, initializing a new one.")
        except Exception as e:
            print(f"Error loading existing JSON: {e}. Initializing a new one.")
    return initial_data

def _create_rate_entry(scraped_date, usd_value, eur_value):
    """Creates a standardized dictionary for a rate entry."""
    return {
        "date": scraped_date.isoformat(),
        "usd_bcv": usd_value,
        "eur_bcv": eur_value
    }

def _should_update_rate_entry(existing_rate_entry, new_date_str):
    """
    Checks if an existing rate entry needs to be updated with a new date.
    Returns True if there is no existing entry or if the date is different.
    """
    return not existing_rate_entry or existing_rate_entry.get("date") != new_date_str

def _process_and_update_rates(json_data, scraped_data, today_local):
    """
    Applies rollover logic and then integrates scraped data into json_data.
    Returns the updated json_data dictionary.
    """
    # Step 1: Apply Rollover based on time
    # The previous day's current_rate remains valid until a new rate for today
    # (either by rollover or scrape) replaces it. It's not automatically cleared
    # just because its date is before 'today' on a weekend.
    if json_data["next_rate"] and json_data["next_rate"].get("date") == today_local.isoformat():
        print(f"Promoting next_rate ({json_data['next_rate']['date']}) to current_rate.")
        json_data["current_rate"] = json_data["next_rate"]
        json_data["next_rate"] = None
    
    # Step 2: Integrate Scraped Data
    if not (scraped_data and scraped_data["scraped_date"] and \
            isinstance(scraped_data["usd_bcv"], (int, float)) and \
            isinstance(scraped_data["eur_bcv"], (int, float))):
        print("Incomplete or invalid scraped data (USD/EUR not numeric). Specific rates not updated.")
        return json_data # Return current data if scraped data is invalid

    scraped_date = scraped_data["scraped_date"]

	# Truncate to two decimal places
    usd_truncated = float(int(scraped_data["usd_bcv"] * 100)) / 100
    eur_truncated = float(int(scraped_data["eur_bcv"] * 100)) / 100

    rate_data_to_save = _create_rate_entry(
        scraped_date,
        usd_truncated,
        eur_truncated
    )
    scraped_date_str = scraped_date.isoformat()

    if scraped_date == today_local:
        if _should_update_rate_entry(json_data["current_rate"], scraped_date_str):
            print(f"Updating current_rate with today's rate: {scraped_date_str}")
            json_data["current_rate"] = rate_data_to_save
        else:
            print(f"current_rate already contains today's rate ({scraped_date_str}). No update.")
    elif scraped_date > today_local: # Rate is for a future day (next business day)
        # Since the configured site publishes the rate for the *next* business day,
        # if scraped_date is > today_local, it will always be the next_rate.
        if _should_update_rate_entry(json_data["next_rate"], scraped_date_str):
            print(f"Updating next_rate with future rate: {scraped_date_str}")
            json_data["next_rate"] = rate_data_to_save
        else:
            print(f"next_rate already contains rate for {scraped_date_str}. No update.")
    else: # scraped_date < today_local (past rate)
        print(f"Scraped date ({scraped_date_str}) is older than today ({today_local}). Ignoring.")

    return json_data

def update_json_file(scraped_data):
    """
    Manages the complete cycle of updating the JSON file:
    loads, processes rates, and saves changes.
    """
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(current_file_dir)

    output_dir = os.path.join(project_root_dir, 'data')
    output_file = os.path.join(output_dir, 'currency_values.json')
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load existing data or initialize
    json_data = _load_or_initialize_json(output_file)
    today_local = get_current_local_date()

    # 2. Process and update rates (core logic)
    json_data = _process_and_update_rates(json_data, scraped_data, today_local)

    # 3. Save updated data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    print(f"JSON file updated at {output_file}")