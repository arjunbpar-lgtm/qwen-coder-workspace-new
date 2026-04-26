"""
Monthly Distribution Screen.

Screen for configuring monthly percentage distribution of annual sales.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class MonthlyDistributionScreen(ttk.Frame):
    """
    Screen for configuring monthly distribution.
    
    Features:
    - Table with Month | Percentage | Amount | Generate Button
    - Total percentage must equal 100
    - Total amount must equal annual sales exactly
    - Editing percentage updates amount
    - Editing amount updates percentage
    - Indicator bar showing balance
    """
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Variables
        self.months = [
            "April", "May", "June", "July", "August", "September",
            "October", "November", "December", "January", "February", "March"
        ]
        
        self.percentage_vars = []
        self.amount_vars = []
        self.entry_widgets = []
        self.amount_entry_widgets = []
        
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
            text="Monthly Distribution",
            font=('Helvetica', 16, 'bold')
        ).grid(row=0, column=0)
        
        ttk.Label(
            title_frame,
            text="Configure how sales are distributed across months",
            font=('Helvetica', 10)
        ).grid(row=1, column=0, pady=5)
        
        # Content frame
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create table frame
        table_frame = ttk.LabelFrame(content_frame, text="Monthly Breakdown", padding="10")
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        
        # Header row
        ttk.Label(table_frame, text="Month", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W
        )
        ttk.Label(table_frame, text="Percentage", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )
        ttk.Label(table_frame, text="Amount (₹)", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=2, padx=5, pady=5, sticky=tk.W
        )
        ttk.Label(table_frame, text="Generate", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=3, padx=5, pady=5, sticky=tk.W
        )
        
        # Create rows for each month
        for i, month in enumerate(self.months):
            row = i + 1
            
            # Month name
            ttk.Label(table_frame, text=month).grid(
                row=row, column=0, padx=5, pady=3, sticky=tk.W
            )
            
            # Percentage entry
            pct_var = tk.StringVar(value="8.33")
            self.percentage_vars.append(pct_var)
            
            pct_entry = ttk.Entry(table_frame, textvariable=pct_var, width=10)
            pct_entry.bind('<FocusOut>', lambda e, idx=i: self._on_percentage_change(idx))
            pct_entry.grid(row=row, column=1, padx=5, pady=3)
            self.entry_widgets.append(pct_entry)
            
            # Amount entry
            amt_var = tk.StringVar(value="0")
            self.amount_vars.append(amt_var)
            
            amt_entry = ttk.Entry(table_frame, textvariable=amt_var, width=15)
            amt_entry.bind('<FocusOut>', lambda e, idx=i: self._on_amount_change(idx))
            amt_entry.grid(row=row, column=2, padx=5, pady=3)
            self.amount_entry_widgets.append(amt_entry)
            
            # Generate button
            gen_btn = ttk.Button(
                table_frame,
                text="Generate",
                command=lambda idx=i: self._generate_month(idx),
                width=10
            )
            gen_btn.grid(row=row, column=3, padx=5, pady=3)
        
        # Indicator frame
        indicator_frame = ttk.LabelFrame(content_frame, text="Distribution Status", padding="10")
        indicator_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        indicator_frame.columnconfigure(1, weight=1)
        
        # Percentage balance
        ttk.Label(indicator_frame, text="Percentage Balance:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.pct_balance_var = tk.StringVar(value="100.00%")
        self.pct_balance_label = ttk.Label(
            indicator_frame,
            textvariable=self.pct_balance_var,
            font=('Helvetica', 11, 'bold'),
            foreground='green'
        )
        self.pct_balance_label.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Amount balance
        ttk.Label(indicator_frame, text="Amount Balance:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.amt_balance_var = tk.StringVar(value="₹0.00")
        self.amt_balance_label = ttk.Label(
            indicator_frame,
            textvariable=self.amt_balance_var,
            font=('Helvetica', 11, 'bold'),
            foreground='green'
        )
        self.amt_balance_label.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
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
        
        self.proceed_btn = ttk.Button(
            button_frame,
            text="Proceed →",
            command=self.proceed,
            width=15,
            state=tk.DISABLED
        )
        self.proceed_btn.grid(row=0, column=1, padx=10)
        
        # Initialize amounts
        self._update_all_amounts()
        self._update_balances()
    
    def _on_percentage_change(self, index):
        """Handle percentage change - update corresponding amount."""
        try:
            pct = float(self.percentage_vars[index].get() or 0)
            annual_sales = self.controller.get_annual_sales()
            amount = (pct / 100) * annual_sales
            self.amount_vars[index].set(f"{amount:.2f}")
            self._update_balances()
        except ValueError:
            pass
    
    def _on_amount_change(self, index):
        """Handle amount change - update corresponding percentage."""
        try:
            amount = float(self.amount_vars[index].get().replace(',', '') or 0)
            annual_sales = self.controller.get_annual_sales()
            if annual_sales > 0:
                pct = (amount / annual_sales) * 100
                self.percentage_vars[index].set(f"{pct:.2f}")
            self._update_balances()
        except ValueError:
            pass
    
    def _update_all_amounts(self):
        """Update all amounts based on percentages and annual sales."""
        annual_sales = self.controller.get_annual_sales()
        
        for i in range(12):
            try:
                pct = float(self.percentage_vars[i].get() or 0)
                amount = (pct / 100) * annual_sales
                self.amount_vars[i].set(f"{amount:.2f}")
            except ValueError:
                pass
        
        self._update_balances()
    
    def _update_balances(self):
        """Update percentage and amount balance indicators."""
        try:
            total_pct = sum(float(v.get() or 0) for v in self.percentage_vars)
            pct_balance = 100.0 - total_pct
            
            annual_sales = self.controller.get_annual_sales()
            total_amount = sum(float(v.get().replace(',', '') or 0) for v in self.amount_vars)
            amt_balance = annual_sales - total_amount
            
            # Update percentage balance display
            self.pct_balance_var.set(f"{pct_balance:+.2f}%")
            if abs(pct_balance) < 0.01:
                self.pct_balance_label.configure(foreground='green')
            else:
                self.pct_balance_label.configure(foreground='red')
            
            # Update amount balance display
            self.amt_balance_var.set(f"₹{amt_balance:+,.2f}")
            if abs(amt_balance) < 0.01:
                self.amt_balance_label.configure(foreground='green')
                self.proceed_btn.configure(state=tk.NORMAL)
            else:
                self.amt_balance_label.configure(foreground='red')
                self.proceed_btn.configure(state=tk.DISABLED)
                
        except ValueError:
            self.pct_balance_var.set("Error")
            self.amt_balance_var.set("Error")
            self.proceed_btn.configure(state=tk.DISABLED)
    
    def _generate_month(self, index):
        """Generate entries for a specific month."""
        # Store the selected month index
        self.controller.set_selected_month(index)
        # Navigate to month generator screen
        self.controller.show_screen("month_generator")
    
    def proceed(self):
        """Proceed to next screen after validation."""
        # Check if totals match
        try:
            total_pct = sum(float(v.get() or 0) for v in self.percentage_vars)
            total_amount = sum(float(v.get().replace(',', '') or 0) for v in self.amount_vars)
            annual_sales = self.controller.get_annual_sales()
            
            if abs(total_pct - 100) > 0.01:
                messagebox.showerror(
                    "Validation Error",
                    f"Percentages must sum to 100%. Current total: {total_pct:.2f}%"
                )
                return
            
            if abs(total_amount - annual_sales) > 0.01:
                messagebox.showerror(
                    "Validation Error",
                    f"Amounts must sum to annual sales (₹{annual_sales:,.2f}).\nCurrent total: ₹{total_amount:,.2f}"
                )
                return
            
            # Store distribution data
            distribution = []
            for i in range(12):
                distribution.append({
                    'month': self.months[i],
                    'percentage': float(self.percentage_vars[i].get()),
                    'amount': float(self.amount_vars[i].get().replace(',', ''))
                })
            
            self.controller.set_monthly_distribution(distribution)
            
            # Go to first month generator
            self.controller.set_selected_month(0)
            self.controller.show_screen("month_generator")
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
    
    def go_back(self):
        """Go back to previous screen."""
        self.controller.show_screen("sales_input")
    
    def load_data(self):
        """Load distribution data from controller."""
        distribution = self.controller.get_monthly_distribution()
        if distribution:
            for i, data in enumerate(distribution):
                if i < 12:
                    self.percentage_vars[i].set(f"{data['percentage']:.2f}")
                    self.amount_vars[i].set(f"{data['amount']:,.2f}")
            self._update_balances()
