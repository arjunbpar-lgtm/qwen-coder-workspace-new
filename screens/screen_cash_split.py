"""
Cash Split Utility Screen.

Separate utility for splitting amounts into multiple entries.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random


class CashSplitScreen(ttk.Frame):
    """
    Utility screen for splitting cash amounts into multiple entries.
    
    Features:
    - Split total amount into random entries
    - Each entry ≤ maximum
    - Each entry ≥ minimum
    - Sum(entries) = total amount
    - Export to Excel and Tally XML
    """
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Variables
        self.total_amount_var = tk.StringVar(value="50000")
        self.max_per_entry_var = tk.StringVar(value="10000")
        self.min_per_entry_var = tk.StringVar(value="100")
        self.max_entries_per_day_var = tk.StringVar(value="5")
        self.start_date_var = tk.StringVar(value="01-04-2024")
        self.day_span_var = tk.StringVar(value="30")
        
        self.generated_entries = []
        
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
            text="Cash Split Utility",
            font=('Helvetica', 16, 'bold')
        ).grid(row=0, column=0)
        
        ttk.Label(
            title_frame,
            text="Split a total amount into multiple random entries",
            font=('Helvetica', 10)
        ).grid(row=1, column=0, pady=5)
        
        # Content frame
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        
        # Input frame
        input_frame = ttk.LabelFrame(content_frame, text="Split Parameters", padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        input_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Total Amount
        ttk.Label(input_frame, text="Total Amount (₹):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.total_amount_var, width=20).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=10
        )
        row += 1
        
        # Max per Entry
        ttk.Label(input_frame, text="Maximum per Entry (₹):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.max_per_entry_var, width=20).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=10
        )
        row += 1
        
        # Min per Entry
        ttk.Label(input_frame, text="Minimum per Entry (₹):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.min_per_entry_var, width=20).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=10
        )
        row += 1
        
        # Max Entries per Day
        ttk.Label(input_frame, text="Max Entries per Day:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.max_entries_per_day_var, width=20).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=10
        )
        row += 1
        
        # Start Date
        ttk.Label(input_frame, text="Start Date:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.start_date_var, width=20).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=10
        )
        ttk.Label(input_frame, text="(DD-MM-YYYY)").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )
        row += 1
        
        # Day Span
        ttk.Label(input_frame, text="Day Span:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.day_span_var, width=20).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=10
        )
        ttk.Label(input_frame, text="days").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )
        row += 1
        
        # Preview frame
        preview_frame = ttk.LabelFrame(content_frame, text="Generated Entries Preview", padding="10")
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        columns = ("Date", "Amount", "Narration")
        self.tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        vsb = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(content_frame, textvariable=self.status_var, 
                                      font=('Helvetica', 10, 'bold'))
        self.status_label.grid(row=2, column=0, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, pady=20)
        
        self.generate_btn = ttk.Button(
            button_frame,
            text="Generate Split",
            command=self.generate_split,
            width=20
        )
        self.generate_btn.grid(row=0, column=0, padx=10)
        
        self.export_xml_btn = ttk.Button(
            button_frame,
            text="Export XML",
            command=self.export_xml,
            width=15,
            state=tk.DISABLED
        )
        self.export_xml_btn.grid(row=0, column=1, padx=10)
        
        self.export_excel_btn = ttk.Button(
            button_frame,
            text="Export Excel",
            command=self.export_excel,
            width=15,
            state=tk.DISABLED
        )
        self.export_excel_btn.grid(row=0, column=2, padx=10)
        
        self.back_btn = ttk.Button(
            button_frame,
            text="← Back",
            command=self.go_back,
            width=15
        )
        self.back_btn.grid(row=0, column=3, padx=10)
    
    def generate_split(self):
        """Generate split entries based on parameters."""
        try:
            total = float(self.total_amount_var.get().replace(',', '') or 0)
            max_entry = float(self.max_per_entry_var.get().replace(',', '') or 0)
            min_entry = float(self.min_per_entry_var.get().replace(',', '') or 0)
            max_entries = int(self.max_entries_per_day_var.get() or 5)
            day_span = int(self.day_span_var.get() or 30)
            
            if total <= 0:
                messagebox.showerror("Error", "Total amount must be positive")
                return
            
            if min_entry >= max_entry:
                messagebox.showerror("Error", "Min entry must be less than max entry")
                return
            
            if min_entry * max_entries > total:
                messagebox.showerror("Error", "Cannot satisfy constraints with given parameters")
                return
            
            # Parse start date
            from datetime import datetime, timedelta
            try:
                start_date = datetime.strptime(self.start_date_var.get(), "%d-%m-%Y")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY")
                return
            
            # Generate entries
            self.generated_entries = []
            remaining = total
            current_date = start_date
            entry_num = 0
            
            while remaining > 0 and entry_num < max_entries * day_span:
                days_left = max(1, day_span - (current_date - start_date).days)
                entries_left = min(max_entries, int(remaining // min_entry) if min_entry > 0 else 1)
                
                if entries_left <= 0:
                    entries_left = 1
                
                # Calculate max allowed for this entry
                avg_needed = remaining / entries_left
                entry_max = min(max_entry, avg_needed * 1.5)
                
                # Generate random entry
                entry_min = min(min_entry, remaining / entries_left)
                entry_amount = random.uniform(entry_min, min(entry_max, remaining))
                entry_amount = round(entry_amount, 2)
                
                if entry_amount < min_entry:
                    entry_amount = min_entry
                
                if entry_amount > remaining:
                    entry_amount = remaining
                
                self.generated_entries.append({
                    'Date': current_date.strftime("%Y-%m-%d"),
                    'Amount': entry_amount,
                    'Narration': f"Cash split entry {entry_num + 1}"
                })
                
                remaining -= entry_amount
                entry_num += 1
                
                # Move to next day occasionally
                if random.random() < 0.3:
                    current_date += timedelta(days=1)
            
            # Adjust last entry to match total exactly
            if self.generated_entries:
                total_generated = sum(e['Amount'] for e in self.generated_entries)
                diff = round(total - total_generated, 2)
                if abs(diff) > 0.001:
                    self.generated_entries[-1]['Amount'] += diff
            
            # Update tree
            self._update_tree()
            
            # Enable export buttons
            self.export_xml_btn.configure(state=tk.NORMAL)
            self.export_excel_btn.configure(state=tk.NORMAL)
            
            total_generated = sum(e['Amount'] for e in self.generated_entries)
            self.status_var.set(f"Generated {len(self.generated_entries)} entries totaling ₹{total_generated:,.2f}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate split: {e}")
    
    def _update_tree(self):
        """Update the tree view with generated entries."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for entry in self.generated_entries[:100]:  # Show first 100
            self.tree.insert('', tk.END, values=(
                entry['Date'],
                f"₹{entry['Amount']:,.2f}",
                entry['Narration']
            ))
    
    def export_xml(self):
        """Export entries to Tally XML."""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Save Tally XML File"
            )
            
            if filepath:
                count = self.controller.export_cash_split_xml(
                    filepath, self.generated_entries
                )
                messagebox.showinfo(
                    "Export Successful",
                    f"XML exported successfully!\n\nFile: {filepath}\nEntries: {count}"
                )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export XML: {e}")
    
    def export_excel(self):
        """Export entries to Excel."""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Excel File"
            )
            
            if filepath:
                self.controller.export_cash_split_excel(
                    filepath, self.generated_entries,
                    float(self.total_amount_var.get().replace(',', '') or 0),
                    {
                        'max_per_entry': self.max_per_entry_var.get(),
                        'min_per_entry': self.min_per_entry_var.get(),
                        'max_entries_per_day': self.max_entries_per_day_var.get(),
                        'start_date': self.start_date_var.get(),
                        'day_span': self.day_span_var.get()
                    }
                )
                messagebox.showinfo(
                    "Export Successful",
                    f"Excel exported successfully!\n\nFile: {filepath}"
                )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export Excel: {e}")
    
    def go_back(self):
        """Go back to main menu."""
        self.controller.show_screen("sales_input")
