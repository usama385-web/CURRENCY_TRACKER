import json
import os

CACHE_FILE = "rates_cache.json"

# Default fallback rates if the user is completely offline on the first run
DEFAULT_RATES = {
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.5, 
    "JPY": 155.0, "CAD": 1.36, "AUD": 1.51, "CNY": 7.24
}

def load_cached_rates():
    """Loads currency data from the local cache file, or defaults if none exists."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_RATES
    return DEFAULT_RATES

def save_rates_to_cache(rates_data):
    """Caches newly fetched rates locally onto the hard drive."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(rates_data, f, indent=4)
    except Exception as e:
        print(f"Failed to cache rates: {e}")

def calculate_conversion(amount, from_currency, to_currency, rates):
    """Converts money calculations mathematically using exchange rates."""
    if from_currency not in rates or to_currency not in rates:
        raise ValueError("Selected currency rate not found.")
        
    # Formula: amount_in_usd = amount / from_rate
    # Formula: final_amount = amount_in_usd * to_rate
    amount_in_usd = amount / rates[from_currency]
    return amount_in_usd * rates[to_currency]