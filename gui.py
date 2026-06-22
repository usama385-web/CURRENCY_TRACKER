import tkinter as tk
from tkinter import ttk, messagebox
import queue
import fetcher
import rates

class CurrencyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Currency Converter & Tracker")
        self.geometry("420x350")
        self.resizable(False, False)
        
        # Initialize internal state data
        self.response_queue = queue.Queue()
        self.currency_data = rates.load_cached_rates()
        self.exchange_rates = self.currency_data.get("rates", rates.DEFAULT_RATES)
        self.available_currencies = sorted(list(self.exchange_rates.keys()))
        
        self.create_widgets()
        self.update_ui_rates_display()
        self.check_queue_loop()

    def create_widgets(self):
        # Title Label
        title_lbl = tk.Label(self, text="Live Currency Converter", font=("Arial", 16, "bold"))
        title_lbl.pack(pady=15)
        
        # Input Field Frame
        input_frame = tk.Frame(self)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Amount:", font=("Arial", 11)).grid(row=0, column=0, padx=5)
        self.amount_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
        self.amount_entry.insert(0, "1.00")
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        # Currency Dropdowns Frame
        dropdown_frame = tk.Frame(self)
        dropdown_frame.pack(pady=10)
        
        tk.Label(dropdown_frame, text="From:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.from_dropdown = ttk.Combobox(dropdown_frame, values=self.available_currencies, width=8, state="readonly")
        self.from_dropdown.set("USD")
        self.from_dropdown.grid(row=0, column=1, padx=5)
        
        tk.Label(dropdown_frame, text="To:", font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.to_dropdown = ttk.Combobox(dropdown_frame, values=self.available_currencies, width=8, state="readonly")
        self.to_dropdown.set("EUR")
        self.to_dropdown.grid(row=0, column=3, padx=5)
        
        # Action Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        
        self.convert_btn = tk.Button(btn_frame, text="Convert", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", command=self.perform_conversion, width=12)
        self.convert_btn.grid(row=0, column=0, padx=10)
        
        self.refresh_btn = tk.Button(btn_frame, text="Refresh Rates", font=("Arial", 10), command=self.sync_live_rates, width=12)
        self.refresh_btn.grid(row=0, column=1, padx=10)
        
        # Output Text Card
        self.result_lbl = tk.Label(self, text="Result will appear here", font=("Arial", 13, "italic"), fg="#333")
        self.result_lbl.pack(pady=10)
        
        self.status_lbl = tk.Label(self, text="Using offline cached rates", font=("Arial", 8), fg="gray")
        self.status_lbl.pack(side="bottom", fill="x", pady=5)

    def perform_conversion(self):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric value for the amount.")
            return
            
        from_curr = self.from_dropdown.get()
        to_curr = self.to_dropdown.get()
        
        try:
            result = rates.calculate_conversion(amount, from_curr, to_curr, self.exchange_rates)
            self.result_lbl.config(text=f"{amount:,.2f} {from_curr} = {result:,.2f} {to_curr}", font=("Arial", 13, "bold"), fg="#1A237E")
        except Exception as e:
            messagebox.showerror("Conversion Error", str(e))

    def sync_live_rates(self):
        self.status_lbl.config(text="Fetching live network rates...", fg="blue")
        self.refresh_btn.config(state="disabled")
        fetcher.trigger_rate_fetch(self.response_queue)

    def update_ui_rates_display(self):
        if "time_last_update_utc" in self.currency_data:
            last_time = self.currency_data["time_last_update_utc"][:25]
            self.status_lbl.config(text=f"Rates Updated: {last_time}", fg="green")

    def check_queue_loop(self):
        """Continuously checks the queue for results from the background network thread."""
        try:
            response = self.response_queue.get_nowait()
            self.refresh_btn.config(state="normal")
            
            if response["success"]:
                self.currency_data = response["data"]
                self.exchange_rates = self.currency_data.get("rates", rates.DEFAULT_RATES)
                rates.save_rates_to_cache(self.currency_data)
                
                # Dynamically rebuild lists if new rates added currencies
                self.available_currencies = sorted(list(self.exchange_rates.keys()))
                self.from_dropdown['values'] = self.available_currencies
                self.to_dropdown['values'] = self.available_currencies
                
                self.update_ui_rates_display()
                messagebox.showinfo("Success", "Exchange rates updated live!")
            else:
                self.status_lbl.config(text="Sync failed. Using cached fallback data.", fg="red")
                messagebox.showwarning("Network Sync Failed", f"Could not retrieve live data:\n{response['error']}\n\nFalling back to old saved rates.")
        except queue.Empty:
            pass
        
        # Run this check every 200ms
        self.after(200, self.check_queue_loop)
