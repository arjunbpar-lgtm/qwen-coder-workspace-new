"""
Summary / Export Screen.

Screen for displaying statistics and exporting data.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class SummaryScreen(ttk.Frame):
    """
    Screen for displaying summary statistics and exporting data.
    
    Features:
    - Statistics display (Total Entries, Average, Highest, Lowest)
    - Audit Consistency Report
    - Export buttons (Tally XML, Excel)
    """
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
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
            text="Summary & Export",
            font=('Helvetica', 16, 'bold')
        ).grid(row=0, column=0)
        
        ttk.Label(
            title_frame,
            text="Review statistics and export your data",
            font=('Helvetica', 10)
        ).grid(row=1, column=0, pady=5)
        
        # Content frame
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(content_frame, text="Statistics", padding="15")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        self.total_entries_var = tk.StringVar(value="0")
        self._create_stat_box(stats_frame, 0, "Total Entries", self.total_entries_var)
        
        self.avg_daily_var = tk.StringVar(value="₹0.00")
        self._create_stat_box(stats_frame, 1, "Average Daily Sales", self.avg_daily_var)
        
        self.highest_day_var = tk.StringVar(value="₹0.00")
        self._create_stat_box(stats_frame, 2, "Highest Day", self.highest_day_var)
        
        self.lowest_day_var = tk.StringVar(value="₹0.00")
        self._create_stat_box(stats_frame, 3, "Lowest Day", self.lowest_day_var)
        
        # Audit Report frame
        audit_frame = ttk.LabelFrame(content_frame, text="Audit Consistency Report", padding="15")
        audit_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        audit_frame.columnconfigure(1, weight=1)
        
        self.audit_results = {}
        
        row = 0
        checks = [
            ("annual_total_check", "Annual total = Monthly totals"),
            ("monthly_total_check", "Monthly totals = Daily totals"),
            ("leave_days_check", "Leave days respected"),
            ("value_limits_check", "Value limits respected")
        ]
        
        for var_name, label in checks:
            ttk.Label(audit_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=5)
            result_var = tk.StringVar(value="Pending")
            self.audit_results[var_name] = result_var
            result_label = ttk.Label(audit_frame, textvariable=result_var, font=('Helvetica', 10, 'bold'))
            result_label.grid(row=row, column=1, sticky=tk.W, pady=5, padx=20)
            row += 1
        
        # Export buttons frame
        export_frame = ttk.LabelFrame(content_frame, text="Export Options", padding="15")
        export_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        export_frame.columnconfigure((0, 1), weight=1)
        
        self.export_xml_btn = ttk.Button(
            export_frame,
            text="Export Tally XML",
            command=self.export_tally_xml,
            width=25
        )
        self.export_xml_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.export_excel_btn = ttk.Button(
            export_frame,
            text="Export Excel",
            command=self.export_excel,
            width=25
        )
        self.export_excel_btn.grid(row=0, column=1, padx=10, pady=10)
        
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
    
    def _create_stat_box(self, parent, col, label, var):
        """Create a statistics display box."""
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=col, padx=10, pady=5, sticky=(tk.W, tk.E))
        frame.columnconfigure(0, weight=1)
        
        ttk.Label(frame, text=label, font=('Helvetica', 9)).pack()
        ttk.Label(frame, textvariable=var, font=('Helvetica', 14, 'bold'), 
                 foreground='blue').pack()
    
    def load_statistics(self):
        """Load and display statistics from controller."""
        stats = self.controller.get_statistics()
        
        self.total_entries_var.set(str(stats.get('total_entries', 0)))
        self.avg_daily_var.set(f"₹{stats.get('avg_daily', 0):,.2f}")
        self.highest_day_var.set(f"₹{stats.get('highest_day', 0):,.2f}")
        self.lowest_day_var.set(f"₹{stats.get('lowest_day', 0):,.2f}")
        
        # Run audit checks
        self.run_audit_checks()
    
    def run_audit_checks(self):
        """Run audit consistency checks."""
        audit = self.controller.run_audit_checks()
        
        for check_name, result in audit.items():
            if check_name in self.audit_results:
                if result['passed']:
                    self.audit_results[check_name].set("✓ Pass")
                else:
                    self.audit_results[check_name].set("✗ Fail")
    
    def export_tally_xml(self):
        """Export data to Tally XML format."""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Save Tally XML File"
            )
            
            if filepath:
                count = self.controller.export_to_tally_xml(filepath)
                messagebox.showinfo(
                    "Export Successful",
                    f"Tally XML exported successfully!\n\nFile: {filepath}\nVouchers: {count}"
                )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export XML: {e}")
    
    def export_excel(self):
        """Export data to Excel format."""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Excel File"
            )
            
            if filepath:
                self.controller.export_to_excel(filepath)
                messagebox.showinfo(
                    "Export Successful",
                    f"Excel file exported successfully!\n\nFile: {filepath}"
                )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export Excel: {e}")
    
    def go_back(self):
        """Go back to preview screen."""
        self.controller.show_screen("preview")
