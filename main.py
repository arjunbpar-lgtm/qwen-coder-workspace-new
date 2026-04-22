"""
Sales Ledger Generator - Main Application

A desktop utility for accountants to generate realistic yearly sales
ledger entries and export them to Excel and TallyPrime XML format.

Usage:
    python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import threading
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator import SalesLedgerGenerator
from xml_converter import TallyXMLConverter
from utils import get_preset_weights


class SalesLedgerApp:
    """
    Main Tkinter application for the Sales Ledger Generator.
    
    Provides a GUI interface for:
    - Entering annual sales parameters
    - Generating ledger entries
    - Exporting to Excel
    - Generating Tally XML vouchers
    """
    
    def __init__(self, root):
        """
        Initialize the application window and widgets.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Sales Ledger Generator")
        self.root.geometry("750x800")
        self.root.resizable(True, True)
        
        # Store generated data
        self.monthly_df = None
        self.ledger_df = None
        
        # Declare variables before creating widgets
        self.annual_sales_var = tk.StringVar(value="1200000")
        self.min_daily_var = tk.StringVar(value="1000")
        self.max_daily_var = tk.StringVar(value="10000")
        self.fy_start_var = tk.StringVar(value="01-04-2024")
        self.distribution_mode_var = tk.StringVar(value="Fruit Wholesale")
        self.entry_mode_var = tk.StringVar(value="Daily Summary")
        self.ledger_name_var = tk.StringVar(value="Cash")
        self.company_name_var = tk.StringVar(value="My Company")
        self.voucher_type_var = tk.StringVar(value="Sales")
        self.gst_var = tk.BooleanVar(value=False)
        self.gst_rate_var = tk.StringVar(value="18")
        self.gst_ledger_var = tk.StringVar(value="GST Payable")
        
        # Create weight spinboxes list
        self.weight_spinboxes = []
        
        # Setup UI
        self._create_widgets()
        self._configure_styles()
    
    def _configure_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure label font
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 11, 'bold'))
        style.configure('Status.TLabel', font=('Courier', 9))
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Sales Ledger Generator", 
            style='Title.TLabel'
        )
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 20))
        row += 1
        
        # === Input Section ===
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        input_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        input_frame.columnconfigure(1, weight=1)
        
        # Annual Sales Amount
        row_input = 0
        ttk.Label(input_frame, text="Annual Sales Amount (₹):").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        self.annual_sales_entry = ttk.Entry(input_frame, textvariable=self.annual_sales_var, width=20)
        self.annual_sales_entry.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row_input += 1
        
        # Minimum Daily Sale
        ttk.Label(input_frame, text="Minimum Daily Sale (₹):").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        self.min_daily_entry = ttk.Entry(input_frame, textvariable=self.min_daily_var, width=20)
        self.min_daily_entry.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row_input += 1
        
        # Maximum Daily Sale
        ttk.Label(input_frame, text="Maximum Daily Sale (₹):").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        self.max_daily_entry = ttk.Entry(input_frame, textvariable=self.max_daily_var, width=20)
        self.max_daily_entry.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row_input += 1
        
        # Financial Year Start Date
        ttk.Label(input_frame, text="Financial Year Start:").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        self.fy_start_entry = ttk.Entry(input_frame, textvariable=self.fy_start_var, width=20)
        self.fy_start_entry.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(input_frame, text="(DD-MM-YYYY)").grid(row=row_input, column=2, sticky=tk.W, padx=5)
        row_input += 1
        
        # Distribution Preset
        ttk.Label(input_frame, text="Distribution Preset:").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        dist_combo = ttk.Combobox(
            input_frame, 
            textvariable=self.distribution_mode_var,
            values=["Uniform", "Fruit Wholesale", "Textiles", "Electronics", "FMCG", "Custom"],
            state="readonly",
            width=17
        )
        dist_combo.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        dist_combo.bind("<<ComboboxSelected>>", self._on_distribution_change)
        row_input += 1
        
        # Custom Monthly Weights Frame
        self.custom_weights_frame = ttk.LabelFrame(input_frame, text="Custom Monthly Weights", padding="10")
        self.custom_weights_frame.grid(row=row_input, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.custom_weights_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        # Create spinboxes for each month
        months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
        for i, month in enumerate(months):
            row_idx = i // 4
            col_idx = i % 4
            label = ttk.Label(self.custom_weights_frame, text=f"{month}:")
            label.grid(row=row_idx*2, column=col_idx, sticky=tk.W)
            spinbox = ttk.Spinbox(self.custom_weights_frame, from_=1, to=100, width=5, increment=1)
            spinbox.set(8)
            spinbox.grid(row=row_idx*2+1, column=col_idx, sticky=(tk.W, tk.E), pady=2)
            self.weight_spinboxes.append(spinbox)
        
        # Initially hide the custom weights frame
        self.custom_weights_frame.grid_remove()
        row_input += 1
        
        # Entry Mode
        ttk.Label(input_frame, text="Entry Mode:").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        entry_combo = ttk.Combobox(
            input_frame,
            textvariable=self.entry_mode_var,
            values=["Daily Summary", "Multiple Entries Per Day"],
            state="readonly",
            width=17
        )
        entry_combo.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row_input += 1
        
        # Ledger Name
        ttk.Label(input_frame, text="Ledger Name:").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        self.ledger_name_entry = ttk.Entry(input_frame, textvariable=self.ledger_name_var, width=20)
        self.ledger_name_entry.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row_input += 1
        
        # Company Name
        ttk.Label(input_frame, text="Company Name:").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        self.company_name_entry = ttk.Entry(input_frame, textvariable=self.company_name_var, width=20)
        self.company_name_entry.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row_input += 1
        
        # Voucher Type
        ttk.Label(input_frame, text="Voucher Type:").grid(
            row=row_input, column=0, sticky=tk.W, pady=5
        )
        voucher_combo = ttk.Combobox(
            input_frame,
            textvariable=self.voucher_type_var,
            values=["Sales", "Receipt", "Journal"],
            state="readonly",
            width=17
        )
        voucher_combo.grid(row=row_input, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row_input += 1
        
        # GST Applicable
        self.gst_checkbutton = ttk.Checkbutton(
            input_frame,
            text="GST Applicable",
            variable=self.gst_var,
            command=self._on_gst_change
        )
        self.gst_checkbutton.grid(row=row_input, column=0, sticky=tk.W, pady=5)
        row_input += 1
        
        # GST Frame
        self.gst_frame = ttk.Frame(input_frame)
        self.gst_frame.grid(row=row_input, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.gst_frame.columnconfigure(1, weight=1)
        
        # GST Rate
        ttk.Label(self.gst_frame, text="GST Rate:").grid(row=0, column=0, sticky=tk.W, pady=2)
        gst_rate_combo = ttk.Combobox(
            self.gst_frame,
            textvariable=self.gst_rate_var,
            values=["5", "12", "18", "28"],
            state="readonly",
            width=5
        )
        gst_rate_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        ttk.Label(self.gst_frame, text="%").grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # GST Ledger Name
        ttk.Label(self.gst_frame, text="GST Ledger Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.gst_ledger_entry = ttk.Entry(self.gst_frame, textvariable=self.gst_ledger_var, width=20)
        self.gst_ledger_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        # Initially hide the GST frame
        self.gst_frame.grid_remove()
        row_input += 1
        
        row += 1
        
        # === Buttons Section ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=15)
        
        self.generate_btn = ttk.Button(
            button_frame,
            text="Generate Ledger",
            command=self._generate_ledger,
            width=20
        )
        self.generate_btn.grid(row=0, column=0, padx=5)
        
        self.export_excel_btn = ttk.Button(
            button_frame,
            text="Export Excel",
            command=self._export_excel,
            width=20,
            state=tk.DISABLED
        )
        self.export_excel_btn.grid(row=0, column=1, padx=5)
        
        self.generate_xml_btn = ttk.Button(
            button_frame,
            text="Generate XML",
            command=self._generate_xml,
            width=20,
            state=tk.DISABLED
        )
        self.generate_xml_btn.grid(row=0, column=2, padx=5)
        
        row += 1
        
        # === Status Section ===
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Status text widget with scrollbar
        self.status_text = tk.Text(
            status_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            font=('Courier', 9),
            state=tk.DISABLED
        )
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        row += 1
        
        # === Preview Section ===
        self.preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        self.preview_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.preview_frame.columnconfigure(0, weight=1)
        
        # Monthly Summary Treeview
        ttk.Label(self.preview_frame, text="Monthly Distribution", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Create frame for monthly treeview with scrollbar
        monthly_tree_frame = ttk.Frame(self.preview_frame)
        monthly_tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        monthly_tree_frame.columnconfigure(0, weight=1)
        monthly_tree_frame.rowconfigure(0, weight=1)
        
        self.monthly_tree = ttk.Treeview(
            monthly_tree_frame,
            columns=("Month", "Percentage", "Amount"),
            show='headings',
            height=12
        )
        self.monthly_tree.heading("Month", text="Month")
        self.monthly_tree.heading("Percentage", text="Percentage")
        self.monthly_tree.heading("Amount", text="Amount")
        
        # Set column widths
        self.monthly_tree.column("Month", width=100)
        self.monthly_tree.column("Percentage", width=80)
        self.monthly_tree.column("Amount", width=120)
        
        # Scrollbar for monthly treeview
        monthly_scrollbar = ttk.Scrollbar(monthly_tree_frame, orient=tk.VERTICAL, command=self.monthly_tree.yview)
        self.monthly_tree.configure(yscrollcommand=monthly_scrollbar.set)
        
        self.monthly_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        monthly_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Sample Entries Treeview
        ttk.Label(self.preview_frame, text="Sample Entries (first 5 / last 5)", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        # Create frame for sample entries treeview with scrollbar
        sample_tree_frame = ttk.Frame(self.preview_frame)
        sample_tree_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sample_tree_frame.columnconfigure(0, weight=1)
        sample_tree_frame.rowconfigure(0, weight=1)
        
        self.sample_tree = ttk.Treeview(
            sample_tree_frame,
            columns=("Date", "VoucherNo", "Ledger", "Amount"),
            show='headings',
            height=10
        )
        self.sample_tree.heading("Date", text="Date")
        self.sample_tree.heading("VoucherNo", text="Voucher No")
        self.sample_tree.heading("Ledger", text="Ledger")
        self.sample_tree.heading("Amount", text="Amount")
        
        # Set column widths
        self.sample_tree.column("Date", width=100)
        self.sample_tree.column("VoucherNo", width=90)
        self.sample_tree.column("Ledger", width=100)
        self.sample_tree.column("Amount", width=100)
        
        # Scrollbar for sample treeview
        sample_scrollbar = ttk.Scrollbar(sample_tree_frame, orient=tk.VERTICAL, command=self.sample_tree.yview)
        self.sample_tree.configure(yscrollcommand=sample_scrollbar.set)
        
        self.sample_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sample_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Initially hide the preview frame
        self.preview_frame.grid_remove()
    
    def _on_distribution_change(self, event=None):
        """Handle change in distribution preset selection."""
        preset = self.distribution_mode_var.get()
        if preset == "Custom":
            self.custom_weights_frame.grid()
        else:
            self.custom_weights_frame.grid_remove()
    
    def _on_gst_change(self):
        """Handle change in GST applicable checkbox."""
        if self.gst_var.get():
            self.gst_frame.grid()
        else:
            self.gst_frame.grid_remove()
    
    def _log_status(self, message: str):
        """
        Add a message to the status log.
        
        Uses root.after() for thread-safe UI updates.
        
        Args:
            message: Message to display
        """
        def update():
            self.status_text.configure(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.status_text.see(tk.END)
            self.status_text.configure(state=tk.DISABLED)
        
        # Use after() for thread-safe UI updates
        self.root.after(0, update)
    
    def _clear_status(self):
        """Clear the status log."""
        self.status_text.configure(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.configure(state=tk.DISABLED)
    
    def _validate_inputs(self) -> bool:
        """
        Validate all input fields.
        
        Returns:
            True if all inputs are valid, False otherwise
        """
        try:
            annual_sales = float(self.annual_sales_var.get())
            min_daily = float(self.min_daily_var.get())
            max_daily = float(self.max_daily_var.get())
            
            if annual_sales <= 0:
                messagebox.showerror("Validation Error", "Annual sales must be positive")
                return False
            
            if min_daily <= 0 or max_daily <= 0:
                messagebox.showerror("Validation Error", "Daily sale limits must be positive")
                return False
            
            if min_daily > max_daily:
                messagebox.showerror("Validation Error", 
                    "Minimum daily sale cannot exceed maximum daily sale")
                return False
            
            # Parse date
            fy_start_str = self.fy_start_var.get()
            try:
                fy_start = datetime.strptime(fy_start_str, "%d-%m-%Y")
            except ValueError:
                messagebox.showerror("Validation Error", 
                    "Invalid date format. Use DD-MM-YYYY")
                return False
            
            # Validate ledger name
            ledger_name = self.ledger_name_var.get().strip()
            if not ledger_name:
                messagebox.showerror("Validation Error", "Ledger name cannot be empty")
                return False
                
            # Validate company name
            company_name = self.company_name_var.get().strip()
            if not company_name:
                messagebox.showerror("Validation Error", "Company name cannot be empty")
                return False
                
            # Validate GST settings if enabled
            if self.gst_var.get():
                gst_ledger_name = self.gst_ledger_var.get().strip()
                if not gst_ledger_name:
                    messagebox.showerror("Validation Error", "GST ledger name cannot be empty when GST is enabled")
                    return False
                    
            # Validate custom weights if custom preset is selected
            if self.distribution_mode_var.get() == "Custom":
                weights = []
                for spinbox in self.weight_spinboxes:
                    try:
                        val = int(spinbox.get())
                        if val < 1 or val > 100:
                            messagebox.showerror("Validation Error", 
                                "Custom weights must be between 1 and 100")
                            return False
                        weights.append(val)
                    except ValueError:
                        messagebox.showerror("Validation Error", 
                            "Custom weights must be integers")
                        return False
                        
                if sum(weights) <= 0:
                    messagebox.showerror("Validation Error", 
                        "Sum of custom weights must be greater than 0")
                    return False
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid input: {e}")
            return False
    
    def _get_parameters(self) -> dict:
        """
        Extract parameters from UI fields.
        
        Returns:
            Dictionary of parameter values
        """
        fy_start_str = self.fy_start_var.get()
        fy_start = datetime.strptime(fy_start_str, "%d-%m-%Y")
        
        distribution_mode = self.distribution_mode_var.get()
        entry_mode = "daily_summary" if self.entry_mode_var.get() == "Daily Summary" else "multiple_entries"
        
        # Determine custom weights based on preset
        custom_weights = None
        if distribution_mode == "Custom":
            custom_weights = [int(s.get()) for s in self.weight_spinboxes]
        
        return {
            "annual_sales": float(self.annual_sales_var.get()),
            "min_daily_sale": float(self.min_daily_var.get()),
            "max_daily_sale": float(self.max_daily_var.get()),
            "fy_start_date": fy_start,
            "distribution_preset": distribution_mode,
            "custom_weights": custom_weights,
            "entry_mode": entry_mode,
            "ledger_name": self.ledger_name_var.get().strip(),
            "company_name": self.company_name_var.get().strip(),
            "voucher_type": self.voucher_type_var.get(),
            "gst_enabled": self.gst_var.get(),
            "gst_rate": float(self.gst_rate_var.get()),
            "gst_ledger_name": self.gst_ledger_var.get().strip()
        }
    
    def _populate_preview(self, monthly_df, ledger_df):
        """
        Populate the preview treeviews with data.
        
        Args:
            monthly_df: DataFrame containing monthly distribution
            ledger_df: DataFrame containing ledger entries
        """
        # Clear existing data
        for item in self.monthly_tree.get_children():
            self.monthly_tree.delete(item)
        
        for item in self.sample_tree.get_children():
            self.sample_tree.delete(item)
        
        # Populate monthly treeview
        for _, row in monthly_df.iterrows():
            self.monthly_tree.insert("", tk.END, values=(
                row['Month'],
                f"{row['Percentage']:.1f}%",
                f"₹{row['Amount']:,.2f}"
            ))
        
        # Populate sample entries treeview
        if len(ledger_df) > 0:
            # First 5 rows
            first_5 = ledger_df.head(5)
            for idx, row in first_5.iterrows():
                voucher_no = f"SL-{idx+1:05d}"
                self.sample_tree.insert("", tk.END, values=(
                    row['Date'].strftime('%d-%m-%Y'),
                    voucher_no,
                    row['Ledger'],
                    f"₹{row['Amount']:,.2f}"
                ))
            
            # Add separator if more than 10 rows
            if len(ledger_df) > 10:
                self.sample_tree.insert("", tk.END, values=("...", "...", "...", "..."))
            
            # Last 5 rows
            last_5 = ledger_df.tail(5)
            for idx, row in last_5.iterrows():
                voucher_no = f"SL-{idx+1:05d}"
                self.sample_tree.insert("", tk.END, values=(
                    row['Date'].strftime('%d-%m-%Y'),
                    voucher_no,
                    row['Ledger'],
                    f"₹{row['Amount']:,.2f}"
                ))
    
    def _generate_ledger(self):
        """Generate sales ledger entries."""
        if not self._validate_inputs():
            return
        
        self._clear_status()
        self._log_status("Starting ledger generation...")
        
        # Disable buttons during generation
        self.generate_btn.configure(state=tk.DISABLED)
        self.progress_bar.start()
        
        # Run in separate thread to keep UI responsive
        def run_generation():
            try:
                params = self._get_parameters()
                
                self._log_status(f"Annual Sales: {params['annual_sales']:,.2f}")
                self._log_status(f"Distribution Preset: {params['distribution_preset']}")
                self._log_status(f"Entry Mode: {params['entry_mode']}")
                self._log_status(f"Ledger: {params['ledger_name']}")
                self._log_status(f"Company: {params['company_name']}")
                self._log_status(f"Voucher Type: {params['voucher_type']}")
                self._log_status(f"GST Enabled: {params['gst_enabled']}")
                if params['gst_enabled']:
                    self._log_status(f"GST Rate: {params['gst_rate']}%")
                    self._log_status(f"GST Ledger: {params['gst_ledger_name']}")
                self._log_status("")
                
                # Create generator
                generator = SalesLedgerGenerator(
                    annual_sales=params['annual_sales'],
                    min_daily_sale=params['min_daily_sale'],
                    max_daily_sale=params['max_daily_sale'],
                    fy_start_date=params['fy_start_date'],
                    distribution_preset=params['distribution_preset'],
                    custom_weights=params['custom_weights'],
                    entry_mode=params['entry_mode'],
                    ledger_name=params['ledger_name']
                )
                
                # Generate ledger
                monthly_df, ledger_df = generator.generate_full_ledger()
                
                # Log monthly summary
                self._log_status("")
                self._log_status("=== Monthly Distribution ===")
                for _, row in monthly_df.iterrows():
                    self._log_status(
                        f"{row['Month']:12s} {row['Percentage']:5.1f}%  {row['Amount']:>12,.2f}"
                    )
                self._log_status("")
                self._log_status(f"Total entries generated: {len(ledger_df)}")
                self._log_status(f"Total amount: {ledger_df['Amount'].sum():,.2f}")
                
                if params['gst_enabled']:
                    gst_amount = ledger_df['Amount'].sum() * params['gst_rate'] / 100
                    self._log_status(f"Estimated GST Amount: {gst_amount:,.2f}")
                
                # Store data for export
                self.monthly_df = monthly_df
                self.ledger_df = ledger_df
                
                # Enable export buttons
                self.root.after(0, lambda: self.export_excel_btn.configure(state=tk.NORMAL))
                self.root.after(0, lambda: self.generate_xml_btn.configure(state=tk.NORMAL))
                
                # Populate preview on main thread
                self.root.after(0, lambda: self._populate_preview(monthly_df, ledger_df))
                
                # Show preview frame and resize window
                self.root.after(0, lambda: self.preview_frame.grid())
                self.root.after(0, lambda: self.root.geometry(""))
                
                self._log_status("")
                self._log_status("Ledger generation completed successfully")
                
            except Exception as e:
                error_msg = f"Error generating ledger: {str(e)}"
                self._log_status(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Generation Error", error_msg))
            finally:
                self.root.after(0, lambda: self.generate_btn.configure(state=tk.NORMAL))
                self.root.after(0, lambda: self.progress_bar.stop())
        
        thread = threading.Thread(target=run_generation, daemon=True)
        thread.start()
    
    def _export_excel(self):
        """Export ledger to Excel file."""
        if self.ledger_df is None:
            messagebox.showwarning("Warning", "Please generate ledger first")
            return
        
        # Default output path
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        default_path = os.path.join(output_dir, "sales_ledger.xlsx")
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialdir=output_dir,
            initialfile="sales_ledger.xlsx",
            title="Save Excel File"
        )
        
        if not file_path:
            return
        
        try:
            self._log_status(f"\nExporting to Excel: {file_path}")
            
            # Export using generator
            params = self._get_parameters()
            generator = SalesLedgerGenerator(
                annual_sales=params['annual_sales'],
                min_daily_sale=params['min_daily_sale'],
                max_daily_sale=params['max_daily_sale'],
                fy_start_date=params['fy_start_date'],
                distribution_preset=params['distribution_preset'],
                custom_weights=params['custom_weights'],
                entry_mode=params['entry_mode'],
                ledger_name=params['ledger_name']
            )
            generator.export_to_excel(self.ledger_df, file_path)
            
            # Log GST info if applicable
            if params['gst_enabled']:
                gst_amount = self.ledger_df['Amount'].sum() * params['gst_rate'] / 100
                self._log_status(f"Estimated GST Amount: {gst_amount:,.2f}")
            
            self._log_status("Excel export completed")
            messagebox.showinfo("Success", f"Excel file saved to:\n{file_path}")
            
        except Exception as e:
            error_msg = f"Error exporting Excel: {str(e)}"
            self._log_status(error_msg)
            messagebox.showerror("Export Error", error_msg)
    
    def _generate_xml(self):
        """Generate Tally XML vouchers."""
        if self.ledger_df is None:
            messagebox.showwarning("Warning", "Please generate ledger first")
            return
        
        # Default output path
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        default_path = os.path.join(output_dir, "tally_vouchers.xml")
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml")],
            initialdir=output_dir,
            initialfile="tally_vouchers.xml",
            title="Save XML File"
        )
        
        if not file_path:
            return
        
        try:
            self._log_status(f"\nGenerating Tally XML...")
            
            # Get parameters
            params = self._get_parameters()
            
            # Create converter with company name
            converter = TallyXMLConverter(
                company_name=params['company_name'],
                sales_ledger_name="Sales",
                cash_ledger_name=params['ledger_name']
            )
            
            # Convert to XML
            voucher_count = converter.convert_ledger_to_xml(
                self.ledger_df,
                file_path,
                company_name=params['company_name'],
                gst_enabled=params['gst_enabled'],
                gst_rate=params['gst_rate'],
                gst_ledger_name=params['gst_ledger_name'],
                voucher_type=params['voucher_type']
            )
            
            self._log_status(f"XML generation completed ({voucher_count} vouchers)")
            messagebox.showinfo("Success", f"Tally XML saved to:\n{file_path}")
            
        except Exception as e:
            error_msg = f"Error generating XML: {str(e)}"
            self._log_status(error_msg)
            messagebox.showerror("XML Error", error_msg)


def main():
    """Main entry point for the application."""
    try:
        root = tk.Tk()
        app = SalesLedgerApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        try:
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\n"
                f"{traceback.format_exc()}"
            )
        except Exception:
            print(f"Fatal error: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
