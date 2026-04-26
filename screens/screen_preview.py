"""
Preview Screen.

Screen for previewing generated entries before export.
"""

import tkinter as tk
from tkinter import ttk


class PreviewScreen(ttk.Frame):
    """
    Screen for previewing generated ledger entries.
    
    Shows first 50 entries in a table format.
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
            text="Preview Entries",
            font=('Helvetica', 16, 'bold')
        ).grid(row=0, column=0)
        
        ttk.Label(
            title_frame,
            text="Review the first 50 generated entries",
            font=('Helvetica', 10)
        ).grid(row=1, column=0, pady=5)
        
        # Content frame
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(content_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ("Date", "Debit Ledger", "Credit Ledger", "Amount", "Narration")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.column("Amount", width=100)
        self.tree.column("Narration", width=250)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
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
            width=15
        )
        self.proceed_btn.grid(row=0, column=1, padx=10)
    
    def load_entries(self):
        """Load entries from controller and display in tree."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        entries = self.controller.get_generated_entries()
        
        # Show first 50 entries
        for entry in entries[:50]:
            self.tree.insert('', tk.END, values=(
                entry.get('Date', ''),
                entry.get('Debit Ledger', ''),
                entry.get('Credit Ledger', ''),
                f"₹{entry.get('Amount', 0):,.2f}",
                entry.get('Narration', '')
            ))
    
    def proceed(self):
        """Proceed to summary/export screen."""
        self.controller.show_screen("summary")
    
    def go_back(self):
        """Go back to month generator screen."""
        self.controller.show_screen("month_generator")
