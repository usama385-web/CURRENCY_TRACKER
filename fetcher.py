import urllib.request
import json
import threading
import queue

# Free, registration-free open API for exchange rates
API_URL = "https://open.er-api.com/v6/latest/USD"

def fetch_live_rates_worker(result_queue):
    """Worker function meant to be run inside a background thread."""
    try:
        # Request data from the API
        with urllib.request.urlopen(API_URL, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                # Pass the successful data back to the main thread via the queue
                result_queue.put({"success": True, "data": data})
            else:
                result_queue.put({"success": False, "error": f"HTTP Error {response.status}"})
    except Exception as e:
        result_queue.put({"success": False, "error": str(e)})

def trigger_rate_fetch(result_queue):
    """Spawns a separate thread so the GUI remains completely responsive."""
    thread = threading.Thread(target=fetch_live_rates_worker, args=(result_queue,), daemon=True)
    thread.start()