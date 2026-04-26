"""
Sales Input Screen.

First screen of the wizard for entering annual sales parameters.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.scrollable_frame import ScrollableFrame
from ui.tooltip import add_tooltip
from ui.help_panel import HelpPanel
from ui.status_bar import StatusBar
from utils.logger import get_logger


class SalesInputScreen(ttk.Frame):
    """
    Sales Input Screen - First step in the ledger generation wizard.
    
    Allows users to enter total annual sales and select the mode of operation.
    Includes validation, tooltips, help panel, and status indicators.
    """
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.logger = get_logger()
        
        # Configure main grid for responsiveness
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main container with scrollable support
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create scrollable frame
        self.scroll_frame = ScrollableFrame(main_container)
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")
        
        # Content container (where actual widgets go)
        content = self.scroll_frame.container
        content.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            content,
            text="Sales Input Screen",
            font=("Helvetica", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Annual Sales Input Section
        sales_frame = ttk.LabelFrame(content, text="Annual Sales Entry", padding=15)
        sales_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        sales_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(
            sales_frame,
            text="Total Annual Sales (₹):",
            font=("Helvetica", 11)
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.annual_sales_var = tk.StringVar()
        self.annual_sales_entry = ttk.Entry(
            sales_frame,
            textvariable=self.annual_sales_var,
            font=("Helvetica", 11),
            width=30
        )
        self.annual_sales_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        add_tooltip(
            self.annual_sales_entry,
            "Enter the total sales amount for the entire financial year.\n"
            "Example: 1200000 for ₹12 Lakhs."
        )
        
        # Mode Selection Section
        mode_frame = ttk.LabelFrame(content, text="Operation Mode", padding=15)
        mode_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        ttk.Label(
            mode_frame,
            text="Select how you want to generate ledgers:",
            font=("Helvetica", 11)
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="build")
        
        build_frame = ttk.Frame(mode_frame)
        build_frame.grid(row=1, column=0, sticky="w", pady=5)
        build_radio = ttk.Radiobutton(
            build_frame,
            text="Build From Annual Sales",
            variable=self.mode_var,
            value="build"
        )
        build_radio.pack(side=tk.LEFT)
        add_tooltip(
            build_radio,
            "Distributes your annual sales across months based on percentages\n"
            "you specify in the next screen."
        )
        
        reconcile_frame = ttk.Frame(mode_frame)
        reconcile_frame.grid(row=2, column=0, sticky="w", pady=5)
        reconcile_radio = ttk.Radiobutton(
            reconcile_frame,
            text="Reconcile From Deposits",
            variable=self.mode_var,
            value="reconcile"
        )
        reconcile_radio.pack(side=tk.LEFT)
        add_tooltip(
            reconcile_radio,
            "Generates entries based on actual bank deposits.\n"
            "(Feature coming soon - currently behaves like Build mode)"
        )
        
        # Navigation Buttons
        btn_frame = ttk.Frame(content)
        btn_frame.grid(row=3, column=0, pady=30)
        
        self.proceed_btn = ttk.Button(
            btn_frame,
            text="Proceed → Monthly Distribution",
            command=self.on_proceed_clicked,
            style="Accent.TButton"
        )
        self.proceed_btn.pack(side=tk.LEFT, padx=10)
        add_tooltip(
            self.proceed_btn,
            "Validate inputs and proceed to configure monthly distribution percentages."
        )
        
        # Help Panel (right side)
        help_panel = HelpPanel(main_container)
        help_panel.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        help_panel.set_content(
            purpose="Enter your total annual sales figure and choose how you want to generate ledger entries.",
            instructions=[
                "Enter the total sales amount for the financial year",
                "Select 'Build From Annual Sales' to distribute manually",
                "Click 'Proceed' to configure monthly percentages"
            ],
            key_rules=[
                "Sales amount must be a positive number",
                "Decimals are allowed (e.g., 1250000.50)",
                "This value will be used as the base for all calculations"
            ]
        )
        
        # Status Bar (bottom)
        self.status_bar = StatusBar(main_container)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.status_bar.set_status("Ready", "Enter annual sales to begin")
        
        # Bind Enter key to proceed
        self.bind('<Return>', lambda e: self.on_proceed_clicked())
        
        self.logger.info("Sales Input Screen initialized")
    
    def on_proceed_clicked(self):
        """Validate inputs and navigate to the next screen."""
        # Clear previous status
        self.status_bar.clear()
        
        # Validate annual sales input
        sales_text = self.annual_sales_var.get().strip()
        
        if not sales_text:
            self.status_bar.set_error("Missing required input: Total Annual Sales")
            messagebox.showerror(
                "Validation Error",
                "Please enter the total annual sales amount.\n\n"
                "This is required to calculate monthly distributions."
            )
            self.annual_sales_entry.focus_set()
            return
        
        try:
            annual_sales = float(sales_text)
            if annual_sales <= 0:
                raise ValueError("Must be positive")
        except ValueError:
            self.status_bar.set_error("Invalid number format")
            messagebox.showerror(
                "Validation Error",
                "Please enter a valid positive number.\n\n"
                "Examples:\n"
                "• 1200000\n"
                "• 1250000.50\n"
                "• 1,200,000 (commas will be removed automatically)"
            )
            self.annual_sales_entry.focus_set()
            return
        
        # Update controller state
        self.controller.set_annual_sales(annual_sales)
        self.controller.set_mode(self.mode_var.get())
        
        # Update status
        self.status_bar.set_valid(f"Annual sales: ₹{annual_sales:,.2f} | Mode: {self.mode_var.get()}")
        
        # Log action
        self.logger.info(
            f"Sales input recorded: ₹{annual_sales:,.2f}, mode: {self.mode_var.get()}"
        )
        
        # Navigate to next screen
        self.controller.show_screen('monthly_distribution')
