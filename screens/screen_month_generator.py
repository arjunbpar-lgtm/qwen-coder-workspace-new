"""
Month Generator Screen.

Screen for generating daily entries for a specific month.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar


class MonthGeneratorScreen(ttk.Frame):
    """
    Screen for generating daily entries for a selected month.
    
    Features:
    - Display selected month and total
    - Min/Max daily sale inputs
    - Calendar control for leave days
    - Ledger fields (Debit, Credit, Narration)
    - Generate Entries button
    - Optional rounding setting
    """
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Variables
        self.min_daily_var = tk.StringVar(value="1000")
        self.max_daily_var = tk.StringVar(value="10000")
        self.debit_ledger_var = tk.StringVar(value="Cash")
        self.credit_ledger_var = tk.StringVar(value="Sales")
        self.narration_var = tk.StringVar(value="Daily sales entry")
        self.rounding_var = tk.BooleanVar(value=False)
        self.leave_days = set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all widgets for this screen."""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Title
        title_frame = ttk.Frame(self)
        title_frame.grid(row=0, column=0, pady=20)
        title_frame.columnconfigure(0, weight=1)
        
        ttk.Label(
            title_frame,
            text="Month Generator",
            font=('Helvetica', 16, 'bold')
        ).grid(row=0, column=0)
        
        ttk.Label(
            title_frame,
            text="Generate daily entries for the selected month",
            font=('Helvetica', 10)
        ).grid(row=1, column=0, pady=5)
        
        # Content frame with scrollbar
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        
        # Month info frame
        info_frame = ttk.LabelFrame(content_frame, text="Month Information", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        info_frame.columnconfigure(1, weight=1)
        
        self.month_label_var = tk.StringVar(value="April 2024")
        ttk.Label(info_frame, text="Selected Month:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, textvariable=self.month_label_var, font=('Helvetica', 11, 'bold')).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=10
        )
        
        self.total_label_var = tk.StringVar(value="₹100,000.00")
        ttk.Label(info_frame, text="Monthly Total:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, textvariable=self.total_label_var, font=('Helvetica', 11, 'bold'), 
                 foreground='blue').grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(content_frame, text="Generation Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        settings_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Min Daily Sale
        ttk.Label(settings_frame, text="Minimum Daily Sale (₹):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(settings_frame, textvariable=self.min_daily_var, width=20).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=10
        )
        row += 1
        
        # Max Daily Sale
        ttk.Label(settings_frame, text="Maximum Daily Sale (₹):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(settings_frame, textvariable=self.max_daily_var, width=20).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=10
        )
        row += 1
        
        # Rounding option
        ttk.Checkbutton(
            settings_frame,
            text="Round to nearest 10",
            variable=self.rounding_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Leave days calendar
        leave_frame = ttk.LabelFrame(settings_frame, text="Leave Days (Non-working days)", padding="10")
        leave_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        leave_frame.columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        ttk.Label(leave_frame, text="Sun", font=('Helvetica', 9, 'bold')).grid(
            row=0, column=0, pady=2
        )
        ttk.Label(leave_frame, text="Mon", font=('Helvetica', 9, 'bold')).grid(
            row=0, column=1, pady=2
        )
        ttk.Label(leave_frame, text="Tue", font=('Helvetica', 9, 'bold')).grid(
            row=0, column=2, pady=2
        )
        ttk.Label(leave_frame, text="Wed", font=('Helvetica', 9, 'bold')).grid(
            row=0, column=3, pady=2
        )
        ttk.Label(leave_frame, text="Thu", font=('Helvetica', 9, 'bold')).grid(
            row=0, column=4, pady=2
        )
        ttk.Label(leave_frame, text="Fri", font=('Helvetica', 9, 'bold')).grid(
            row=0, column=5, pady=2
        )
        ttk.Label(leave_frame, text="Sat", font=('Helvetica', 9, 'bold')).grid(
            row=0, column=6, pady=2
        )
        
        self.leave_checkboxes = []
        day_row = 1
        for day in range(1, 32):
            col = (day - 1) % 7
            if col == 0 and day > 1:
                day_row += 1
            
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(leave_frame, text=str(day), variable=var, width=3)
            cb.grid(row=day_row, column=col, padx=1, pady=1)
            self.leave_checkboxes.append(var)
            
            if day == 31:
                break
        
        # Ledger settings frame
        ledger_frame = ttk.LabelFrame(content_frame, text="Ledger Settings", padding="10")
        ledger_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        ledger_frame.columnconfigure(1, weight=1)
        
        ttk.Label(ledger_frame, text="Debit Ledger:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(ledger_frame, textvariable=self.debit_ledger_var, width=30).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=10
        )
        
        ttk.Label(ledger_frame, text="Credit Ledger:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(ledger_frame, textvariable=self.credit_ledger_var, width=30).grid(
            row=1, column=1, sticky=tk.W, pady=5, padx=10
        )
        
        ttk.Label(ledger_frame, text="Narration:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(ledger_frame, textvariable=self.narration_var, width=30).grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=10
        )
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, pady=20)
        
        self.back_btn = ttk.Button(
            button_frame,
            text="← Back",
            command=self.go_back,
            width=15
        )
        self.back_btn.grid(row=0, column=0, padx=10)
        
        self.generate_btn = ttk.Button(
            button_frame,
            text="Generate Entries",
            command=self.generate_entries,
            width=20
        )
        self.generate_btn.grid(row=0, column=1, padx=10)
        
        self.proceed_btn = ttk.Button(
            button_frame,
            text="Proceed →",
            command=self.proceed,
            width=15,
            state=tk.DISABLED
        )
        self.proceed_btn.grid(row=0, column=2, padx=10)
        
        # Status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(self, textvariable=self.status_var, foreground='green')
        self.status_label.grid(row=3, column=0, pady=5)
    
    def load_month_data(self):
        """Load data for the selected month."""
        month_idx = self.controller.get_selected_month()
        distribution = self.controller.get_monthly_distribution()
        
        if distribution and month_idx < len(distribution):
            month_data = distribution[month_idx]
            self.month_label_var.set(f"{month_data['month']} {datetime.now().year}")
            self.total_label_var.set(f"₹{month_data['amount']:,.2f}")
    
    def generate_entries(self):
        """Generate daily entries for the month."""
        try:
            month_idx = self.controller.get_selected_month()
            distribution = self.controller.get_monthly_distribution()
            
            if not distribution or month_idx >= len(distribution):
                messagebox.showerror("Error", "No month selected")
                return
            
            month_data = distribution[month_idx]
            monthly_total = month_data['amount']
            
            min_daily = float(self.min_daily_var.get().replace(',', '') or 0)
            max_daily = float(self.max_daily_var.get().replace(',', '') or 0)
            
            if min_daily <= 0 or max_daily <= 0:
                messagebox.showerror("Error", "Min/Max daily sale must be positive")
                return
            
            if min_daily > max_daily:
                messagebox.showerror("Error", "Min daily sale cannot exceed max daily sale")
                return
            
            # Get leave days
            self.leave_days = set()
            for i, var in enumerate(self.leave_checkboxes):
                if var.get():
                    self.leave_days.add(i + 1)
            
            # Generate entries using controller
            entries = self.controller.generate_month_entries(
                month_idx=month_idx,
                monthly_total=monthly_total,
                min_daily=min_daily,
                max_daily=max_daily,
                leave_days=self.leave_days,
                debit_ledger=self.debit_ledger_var.get(),
                credit_ledger=self.credit_ledger_var.get(),
                narration=self.narration_var.get(),
                round_to_10=self.rounding_var.get()
            )
            
            if entries:
                self.status_var.set(f"Generated {len(entries)} entries successfully!")
                self.proceed_btn.configure(state=tk.NORMAL)
            else:
                self.status_var.set("")
                messagebox.showwarning("Warning", "No entries generated")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate entries: {e}")
    
    def proceed(self):
        """Proceed to preview screen."""
        self.controller.show_screen("preview")
    
    def go_back(self):
        """Go back to monthly distribution screen."""
        self.controller.show_screen("monthly_distribution")
