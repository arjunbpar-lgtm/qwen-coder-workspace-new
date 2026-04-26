"""
Sales Input Screen.

First screen of the wizard for entering annual sales parameters.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SalesInputScreen(ttk.Frame):
    """
    Screen for entering total annual sales and mode selection.
    
    Fields:
    - Total Annual Sales
    - Mode Selection: Build From Annual Sales / Reconcile From Deposits
    """
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Variables
        self.annual_sales_var = tk.StringVar(value="1200000")
        self.mode_var = tk.StringVar(value="annual")
        
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
            text="Sales Input",
            font=('Helvetica', 16, 'bold')
        ).grid(row=0, column=0)
        
        ttk.Label(
            title_frame,
            text="Enter your annual sales details",
            font=('Helvetica', 10)
        ).grid(row=1, column=0, pady=5)
        
        # Content frame
        content_frame = ttk.LabelFrame(self, text="Sales Parameters", padding="20")
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        content_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Total Annual Sales
        ttk.Label(
            content_frame,
            text="Total Annual Sales (₹):",
            font=('Helvetica', 11)
        ).grid(row=row, column=0, sticky=tk.W, pady=10)
        
        self.annual_sales_entry = ttk.Entry(
            content_frame,
            textvariable=self.annual_sales_var,
            width=30,
            font=('Helvetica', 11)
        )
        self.annual_sales_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=10, padx=10)
        row += 1
        
        # Mode Selection
        ttk.Label(
            content_frame,
            text="Mode:",
            font=('Helvetica', 11)
        ).grid(row=row, column=0, sticky=tk.W, pady=10)
        
        mode_frame = ttk.Frame(content_frame)
        mode_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        ttk.Radiobutton(
            mode_frame,
            text="Build From Annual Sales",
            variable=self.mode_var,
            value="annual"
        ).grid(row=0, column=0, padx=10)
        
        ttk.Radiobutton(
            mode_frame,
            text="Reconcile From Deposits",
            variable=self.mode_var,
            value="deposits"
        ).grid(row=0, column=1, padx=10)
        row += 1
        
        # Info label
        info_label = ttk.Label(
            content_frame,
            text="Note: In 'Build From Annual Sales' mode, you specify the total\n"
                 "and it gets distributed across months. In 'Reconcile From Deposits'\n"
                 "mode, you start with bank deposits and work backwards.",
            foreground='gray',
            justify=tk.LEFT
        )
        info_label.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, pady=20)
        
        self.back_btn = ttk.Button(
            button_frame,
            text="Back",
            command=self.go_back,
            width=15
        )
        self.back_btn.grid(row=0, column=0, padx=10)
        
        self.proceed_btn = ttk.Button(
            button_frame,
            text="Proceed →",
            command=self.proceed,
            width=15
        )
        self.proceed_btn.grid(row=0, column=1, padx=10)
    
    def validate_input(self) -> bool:
        """Validate numeric input for annual sales."""
        try:
            value = self.annual_sales_var.get().strip()
            if not value:
                messagebox.showerror("Validation Error", "Please enter annual sales amount")
                return False
            
            amount = float(value.replace(',', ''))
            if amount <= 0:
                messagebox.showerror("Validation Error", "Annual sales must be positive")
                return False
            
            return True
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid number")
            return False
    
    def proceed(self):
        """Validate and proceed to next screen."""
        if not self.validate_input():
            return
        
        # Store data in controller
        self.controller.set_annual_sales(float(self.annual_sales_var.get().replace(',', '')))
        self.controller.set_mode(self.mode_var.get())
        
        # Navigate to next screen
        self.controller.show_screen("monthly_distribution")
    
    def go_back(self):
        """Go back to previous screen or exit if first screen."""
        messagebox.showinfo("Info", "This is the first screen")
