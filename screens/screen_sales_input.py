"""
Sales Input Screen.

First screen of the wizard for entering annual sales parameters.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.tooltip import Tooltip


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
        # Main container with two columns (content + help)
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)
        
        # Content frame (left side)
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        
        # Help panel (right side)
        help_frame = self._create_help_panel(
            main_frame,
            "Sales Input Screen",
            [
                "Purpose: Enter your total annual sales figure and select the generation mode.",
                "",
                "What to do:",
                "• Enter the total annual sales amount in rupees",
                "• Select 'Build From Annual Sales' to distribute sales across months",
                "• Select 'Reconcile From Deposits' to work backwards from bank deposits",
                "",
                "Key Rules:",
                "• Annual sales must be a positive number",
                "• Commas are optional (e.g., 1,200,000 or 1200000)"
            ]
        )
        help_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(20, 0))
        
        # Title
        title_frame = ttk.Frame(content_frame)
        title_frame.grid(row=0, column=0, pady=(0, 20))
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
        input_frame = ttk.LabelFrame(content_frame, text="Sales Parameters", padding="20")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        input_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Total Annual Sales
        ttk.Label(
            input_frame,
            text="Total Annual Sales (₹):",
            font=('Helvetica', 11)
        ).grid(row=row, column=0, sticky=tk.W, pady=10)
        
        self.annual_sales_entry = ttk.Entry(
            input_frame,
            textvariable=self.annual_sales_var,
            width=30,
            font=('Helvetica', 11)
        )
        self.annual_sales_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=10, padx=10)
        Tooltip(self.annual_sales_entry, "Enter the total annual sales amount. Example: 1200000 for ₹12,00,000")
        row += 1
        
        # Mode Selection
        ttk.Label(
            input_frame,
            text="Mode:",
            font=('Helvetica', 11)
        ).grid(row=row, column=0, sticky=tk.W, pady=10)
        
        mode_frame = ttk.Frame(input_frame)
        mode_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        build_radio = ttk.Radiobutton(
            mode_frame,
            text="Build From Annual Sales",
            variable=self.mode_var,
            value="annual"
        )
        build_radio.grid(row=0, column=0, padx=10)
        Tooltip(build_radio, "Start with annual total and distribute it across months")
        
        reconcile_radio = ttk.Radiobutton(
            mode_frame,
            text="Reconcile From Deposits",
            variable=self.mode_var,
            value="deposits"
        )
        reconcile_radio.grid(row=0, column=1, padx=10)
        Tooltip(reconcile_radio, "Start with bank deposits and reconcile backwards")
        row += 1
        
        # Info label
        info_label = ttk.Label(
            input_frame,
            text="Note: In 'Build From Annual Sales' mode, you specify the total\n"
                 "and it gets distributed across months. In 'Reconcile From Deposits'\n"
                 "mode, you start with bank deposits and work backwards.",
            foreground='gray',
            justify=tk.LEFT
        )
        info_label.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Buttons frame
        button_frame = ttk.Frame(content_frame)
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
        Tooltip(self.proceed_btn, "Validate inputs and proceed to Monthly Distribution screen")
    
    def _create_help_panel(self, parent, title, lines):
        """Create a help panel with formatted text."""
        frame = ttk.LabelFrame(parent, text=title, padding="15", width=280)
        frame.columnconfigure(0, weight=1)
        
        for i, line in enumerate(lines):
            if line.startswith("•"):
                ttk.Label(frame, text=line, foreground='#444444').grid(
                    row=i, column=0, sticky=tk.W, pady=2, padx=(10, 0)
                )
            elif line.startswith("Key Rules:") or line.startswith("What to do:"):
                ttk.Label(frame, text=line, font=('Helvetica', 9, 'bold')).grid(
                    row=i, column=0, sticky=tk.W, pady=(8, 4)
                )
            elif line == "":
                ttk.Label(frame, text="").grid(row=i, column=0)
            else:
                ttk.Label(frame, text=line, wraplength=250).grid(
                    row=i, column=0, sticky=tk.W, pady=2
                )
        
        return frame
    
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
