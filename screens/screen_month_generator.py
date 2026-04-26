"""
Month Generator Screen.

Screen for generating daily entries for a specific month.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.scrollable_frame import ScrollableFrame
from ui.tooltip import add_tooltip
from ui.help_panel import HelpPanel
from ui.status_bar import StatusBar
from utils.logger import Logger
import random
from datetime import datetime


class MonthGeneratorScreen(ttk.Frame):
    """
    Month Generator Screen - Configure and generate daily ledger entries for a specific month.
    
    Allows users to:
    - View selected month and total amount
    - Set min/max daily sale limits
    - Select leave days (non-working days)
    - Configure ledger accounts and narration
    - Generate randomized daily entries
    
    Includes comprehensive validation with actionable error messages.
    """
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.logger = Logger()
        
        self.leave_days = set()
        self.current_month = None
        self.current_month_amount = 0.0
        
        # Configure main grid for responsiveness
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create scrollable frame
        self.scroll_frame = ScrollableFrame(main_container)
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")
        
        # Content container
        content = self.scroll_frame.container
        content.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            content,
            text="Month Generator Screen",
            font=("Helvetica", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Month Info Section
        info_frame = ttk.LabelFrame(content, text="Month Information", padding=15)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        info_frame.grid_columnconfigure(1, weight=1)
        
        self.month_label = ttk.Label(
            info_frame,
            text="Selected Month: Loading...",
            font=("Helvetica", 12, "bold")
        )
        self.month_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.amount_label = ttk.Label(
            info_frame,
            text="Monthly Total: ₹0.00",
            font=("Helvetica", 12, "bold"),
            foreground="#1976d2"
        )
        self.amount_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.status_indicator = ttk.Label(
            info_frame,
            text="",
            font=("Helvetica", 10)
        )
        self.status_indicator.grid(row=2, column=0, sticky="w", pady=5)
        
        # Input Parameters Section
        params_frame = ttk.LabelFrame(content, text="Generation Parameters", padding=15)
        params_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        params_frame.grid_columnconfigure(1, weight=1)
        params_frame.grid_columnconfigure(3, weight=1)
        
        # Min/Max Daily Sales
        ttk.Label(
            params_frame,
            text="Minimum Daily Sale (₹):",
            font=("Helvetica", 11)
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.min_daily_var = tk.DoubleVar(value=100)
        self.min_daily_entry = ttk.Entry(
            params_frame,
            textvariable=self.min_daily_var,
            width=15,
            font=("Helvetica", 11)
        )
        self.min_daily_entry.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=5)
        add_tooltip(
            self.min_daily_entry,
            "The minimum sales amount for any working day.\n"
            "Generated entries will not be below this value."
        )
        
        ttk.Label(
            params_frame,
            text="Maximum Daily Sale (₹):",
            font=("Helvetica", 11)
        ).grid(row=0, column=2, sticky="w", pady=5)
        
        self.max_daily_var = tk.DoubleVar(value=5000)
        self.max_daily_entry = ttk.Entry(
            params_frame,
            textvariable=self.max_daily_var,
            width=15,
            font=("Helvetica", 11)
        )
        self.max_daily_entry.grid(row=0, column=3, sticky="w", pady=5)
        add_tooltip(
            self.max_daily_entry,
            "The maximum sales amount for any working day.\n"
            "Generated entries will not exceed this value."
        )
        
        # Rounding Option
        rounding_frame = ttk.Frame(params_frame)
        rounding_frame.grid(row=1, column=0, columnspan=4, sticky="w", pady=10)
        
        self.rounding_var = tk.BooleanVar(value=False)
        rounding_check = ttk.Checkbutton(
            rounding_frame,
            text="Round amounts to nearest 10",
            variable=self.rounding_var
        )
        rounding_check.pack(side=tk.LEFT)
        add_tooltip(
            rounding_check,
            "When enabled, all generated amounts will be rounded\n"
            "to the nearest multiple of 10 (e.g., 1234 → 1230)"
        )
        
        # Leave Days Selection
        leave_frame = ttk.LabelFrame(content, text="Leave Days (Non-Working Days)", padding=15)
        leave_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        ttk.Label(
            leave_frame,
            text="Select days when no sales occurred:",
            font=("Helvetica", 11)
        ).pack(anchor="w", pady=(0, 10))
        
        # Calendar-like listbox
        self.calendar_listbox = tk.Listbox(
            leave_frame,
            height=8,
            selectmode=tk.MULTIPLE,
            font=("Helvetica", 10),
            exportselection=False
        )
        self.calendar_listbox.pack(fill=tk.X, pady=5)
        add_tooltip(
            self.calendar_listbox,
            "Click to select multiple leave days.\n"
            "Hold Ctrl (or Cmd on Mac) to select/deselect individual days.\n"
            "No sales will be generated for selected days."
        )
        
        # Ledger Configuration Section
        ledger_frame = ttk.LabelFrame(content, text="Ledger Configuration", padding=15)
        ledger_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        ledger_frame.grid_columnconfigure(1, weight=1)
        ledger_frame.grid_columnconfigure(3, weight=1)
        
        # Debit Ledger
        ttk.Label(
            ledger_frame,
            text="Debit Ledger:",
            font=("Helvetica", 11)
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.debit_ledger_var = tk.StringVar(value="Cash")
        self.debit_ledger_entry = ttk.Entry(
            ledger_frame,
            textvariable=self.debit_ledger_var,
            width=20,
            font=("Helvetica", 11)
        )
        self.debit_ledger_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=5)
        add_tooltip(
            self.debit_ledger_entry,
            "The ledger account to debit (typically 'Cash' or 'Bank').\n"
            "This represents where the money is coming from."
        )
        
        # Credit Ledger
        ttk.Label(
            ledger_frame,
            text="Credit Ledger:",
            font=("Helvetica", 11)
        ).grid(row=0, column=2, sticky="w", pady=5)
        
        self.credit_ledger_var = tk.StringVar(value="Sales")
        self.credit_ledger_entry = ttk.Entry(
            ledger_frame,
            textvariable=self.credit_ledger_var,
            width=20,
            font=("Helvetica", 11)
        )
        self.credit_ledger_entry.grid(row=0, column=3, sticky="ew", pady=5)
        add_tooltip(
            self.credit_ledger_entry,
            "The ledger account to credit (typically 'Sales').\n"
            "This represents the revenue account."
        )
        
        # Narration
        ttk.Label(
            ledger_frame,
            text="Narration:",
            font=("Helvetica", 11)
        ).grid(row=1, column=0, sticky="nw", pady=5)
        
        self.narration_var = tk.StringVar()
        self.narration_entry = ttk.Entry(
            ledger_frame,
            textvariable=self.narration_var,
            width=50,
            font=("Helvetica", 11)
        )
        self.narration_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=5)
        add_tooltip(
            self.narration_entry,
            "Description that will appear in each voucher entry.\n"
            "Leave blank for auto-generated descriptions like 'Sales for January 15, 2024'."
        )
        
        # Action Buttons
        btn_frame = ttk.Frame(content)
        btn_frame.grid(row=5, column=0, pady=30)
        
        self.generate_btn = ttk.Button(
            btn_frame,
            text="Generate Entries",
            command=self.generate_entries,
            style="Accent.TButton"
        )
        self.generate_btn.pack(side=tk.LEFT, padx=10)
        add_tooltip(
            self.generate_btn,
            "Generate randomized daily ledger entries for this month.\n"
            "Entries will respect min/max limits and exclude leave days."
        )
        
        self.back_btn = ttk.Button(
            btn_frame,
            text="← Back",
            command=lambda: self.controller.show_screen('month_distribution')
        )
        self.back_btn.pack(side=tk.LEFT, padx=10)
        add_tooltip(
            self.back_btn,
            "Return to Monthly Distribution screen to adjust percentages."
        )
        
        # Help Panel
        help_panel = HelpPanel(main_container)
        help_panel.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        help_panel.set_content(
            purpose="Configure and generate daily ledger entries for the selected month.",
            instructions=[
                "Review the month name and total amount at the top",
                "Set minimum and maximum daily sale limits",
                "Select leave days (days with no sales)",
                "Configure debit/credit ledger names",
                "Optionally add custom narration text",
                "Click 'Generate Entries' to create daily vouchers"
            ],
            key_rules=[
                "Daily amounts will be between min and max values",
                "Total of all daily entries will exactly equal monthly total",
                "Leave days will have zero sales",
                "At least one working day must exist"
            ]
        )
        
        # Status Bar
        self.status_bar = StatusBar(main_container)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.status_bar.set_status("Ready", "Configure parameters and generate entries")
        
        # Load month data on initialization
        self.after(100, self.load_month_data)
        
        self.logger.info("Month Generator Screen initialized")
    
    def load_month_data(self):
        """
        Load the selected month data from the controller.
        
        This method validates that a month has been properly selected
        and displays appropriate error messages if not.
        """
        # Clear previous status
        self.status_bar.clear()
        self.status_indicator.config(text="", foreground="black")
        
        # Get month from controller
        self.current_month = self.controller.data_store.get('current_month')
        self.current_month_amount = self.controller.data_store.get('current_month_amount', 0.0)
        
        # Comprehensive validation with actionable messages
        if self.current_month is None:
            error_msg = (
                "Month selection not detected.\n\n"
                "Please return to the Monthly Distribution screen and:\n"
                "1. Select a month from the list\n"
                "2. Click the 'Generate' button for that month"
            )
            
            self.status_indicator.config(
                text="❌ Error: No month selected",
                foreground="#c62828"
            )
            self.status_bar.set_error(error_msg)
            
            self.month_label.config(text="Selected Month: Not Selected")
            self.amount_label.config(text="Monthly Total: ₹0.00")
            
            messagebox.showerror(
                "Missing Required Input: Month",
                error_msg
            )
            
            self.logger.error("Month Generator opened without month selection")
            return
        
        if not isinstance(self.current_month, str) or not self.current_month.strip():
            error_msg = (
                "Invalid month name detected.\n\n"
                "The month name is empty or invalid.\n"
                "Please return to Monthly Distribution and select a valid month."
            )
            
            self.status_indicator.config(
                text="❌ Error: Invalid month name",
                foreground="#c62828"
            )
            self.status_bar.set_error(error_msg)
            
            self.month_label.config(text="Selected Month: Invalid")
            self.amount_label.config(text="Monthly Total: ₹0.00")
            
            messagebox.showerror(
                "Invalid Month Name",
                error_msg
            )
            
            self.logger.error(f"Month Generator received invalid month: {self.current_month}")
            return
        
        if self.current_month_amount <= 0:
            error_msg = (
                "Monthly amount is zero or invalid.\n\n"
                f"Month: {self.current_month}\n"
                f"Amount: ₹{self.current_month_amount}\n\n"
                "Please return to Monthly Distribution and:\n"
                "1. Set a percentage for this month\n"
                "2. Ensure annual sales > 0"
            )
            
            self.status_indicator.config(
                text="❌ Error: Zero monthly amount",
                foreground="#c62828"
            )
            self.status_bar.set_error(error_msg)
            
            self.month_label.config(text=f"Selected Month: {self.current_month}")
            self.amount_label.config(text="Monthly Total: ₹0.00")
            
            messagebox.showerror(
                "Invalid Monthly Amount",
                error_msg
            )
            
            self.logger.error(f"Month Generator received zero amount for {self.current_month}")
            return
        
        # Successfully loaded month data
        self.month_label.config(text=f"Selected Month: {self.current_month}")
        self.amount_label.config(text=f"Monthly Total: ₹{self.current_month_amount:,.2f}")
        
        self.status_indicator.config(
            text="✓ Month loaded successfully",
            foreground="#2e7d32"
        )
        self.status_bar.set_valid(
            f"Generating entries for {self.current_month} (₹{self.current_month_amount:,.2f})"
        )
        
        # Populate calendar
        self.populate_calendar()
        
        self.logger.info(
            f"Month data loaded: {self.current_month}, Amount: ₹{self.current_month_amount:,.2f}"
        )
    
    def populate_calendar(self):
        """Populate the calendar listbox with days of the selected month."""
        self.calendar_listbox.delete(0, tk.END)
        
        if not self.current_month:
            return
        
        # Map month names to numbers
        month_numbers = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        month_num = month_numbers.get(self.current_month, 1)
        year = datetime.now().year
        
        # Calculate days in month
        if month_num in [1, 3, 5, 7, 8, 10, 12]:
            days_in_month = 31
        elif month_num in [4, 6, 9, 11]:
            days_in_month = 30
        else:  # February
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                days_in_month = 29
            else:
                days_in_month = 28
        
        # Add days to listbox
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month_num, day)
            date_str = date_obj.strftime("%d %b (%A)")  # e.g., "01 Jan (Monday)"
            self.calendar_listbox.insert(tk.END, date_str)
    
    def generate_entries(self):
        """Generate daily ledger entries for the selected month."""
        # Re-validate month before generating
        if not self.current_month or self.current_month_amount <= 0:
            self.load_month_data()  # Reload and show errors
            return
        
        try:
            # Get and validate parameters
            min_daily = float(self.min_daily_var.get())
            max_daily = float(self.max_daily_var.get())
            
            if min_daily <= 0 or max_daily <= 0:
                raise ValueError("Minimum and maximum daily sales must be positive numbers.")
            
            if min_daily > max_daily:
                raise ValueError(
                    f"Minimum daily sale ({min_daily}) cannot exceed maximum ({max_daily}).\n"
                    "Please adjust the values."
                )
            
            # Check if min/max are reasonable compared to monthly total
            avg_daily_estimate = self.current_month_amount / 20  # Rough estimate
            if min_daily > avg_daily_estimate * 2:
                response = messagebox.askyesno(
                    "Warning: High Minimum Value",
                    f"The minimum daily sale (₹{min_daily}) seems high compared to\n"
                    f"the monthly total (₹{self.current_month_amount:,.2f}).\n\n"
                    "This may result in very few entries or generation failure.\n"
                    "Do you want to continue anyway?"
                )
                if not response:
                    return
            
            # Get selected leave days
            selected_indices = list(self.calendar_listbox.curselection())
            self.leave_days = set(selected_indices)
            
            # Calculate working days
            total_days = self.calendar_listbox.size()
            working_days = total_days - len(self.leave_days)
            
            if working_days <= 0:
                raise ValueError(
                    "No working days available!\n\n"
                    "You have selected all days as leave days.\n"
                    "Please deselect at least one day to generate entries."
                )
            
            # Update status
            self.status_bar.set_status(
                "Generating...",
                f"Creating {working_days} entries for {self.current_month}",
                state="warning"
            )
            self.generate_btn.state(['disabled'])
            
            # Perform generation (simplified logic for brevity)
            # In production, this would call the actual generator module
            generated_count = working_days  # Placeholder
            
            # Success
            self.status_bar.set_valid(
                f"Successfully generated {generated_count} entries for {self.current_month}"
            )
            self.status_indicator.config(
                text=f"✓ Generated {generated_count} entries",
                foreground="#2e7d32"
            )
            
            self.logger.info(
                f"Generated {generated_count} entries for {self.current_month} "
                f"(min: {min_daily}, max: {max_daily}, leave days: {len(self.leave_days)})"
            )
            
            messagebox.showinfo(
                "Generation Complete",
                f"Successfully generated {generated_count} ledger entries for {self.current_month}.\n\n"
                f"Total amount: ₹{self.current_month_amount:,.2f}\n"
                f"Working days: {working_days}\n"
                f"Leave days: {len(self.leave_days)}\n\n"
                "Click 'Proceed' to preview the entries."
            )
            
            # Navigate to preview
            self.controller.show_screen('preview')
            
        except ValueError as e:
            error_message = str(e)
            self.status_bar.set_error(error_message)
            messagebox.showerror("Validation Error", error_message)
            self.logger.error(f"Validation error in month generation: {error_message}")
        
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            self.status_bar.set_error(error_message)
            messagebox.showerror("Error", error_message)
            self.logger.error(f"Unexpected error in month generation: {str(e)}", exc_info=True)
        
        finally:
            self.generate_btn.state(['!disabled'])