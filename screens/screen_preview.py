"""
Preview Screen.

Screen for previewing generated entries before export.
"""

import tkinter as tk
from tkinter import ttk
from utils.tooltip import Tooltip


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
            "Preview Entries",
            [
                "Purpose: Review generated entries before proceeding to export.",
                "",
                "What to do:",
                "• Scroll through the list to verify entries",
                "• Check dates, amounts, and narration text",
                "• Click 'Proceed' when satisfied with the data",
                "",
                "Key Rules:",
                "• Only first 50 entries are shown",
                "• All entries will be exported regardless",
                "• Go back to modify if needed"
            ]
        )
        help_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(20, 0))
        
        # Title
        title_frame = ttk.Frame(content_frame)
        title_frame.grid(row=0, column=0, pady=(0, 15))
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
        inner_content = ttk.Frame(content_frame)
        inner_content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        inner_content.columnconfigure(0, weight=1)
        inner_content.rowconfigure(0, weight=1)
        
        # Treeview with scrollbar
        tree_frame = ttk.LabelFrame(inner_content, text="Entries Preview", padding="10")
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
        button_frame = ttk.Frame(content_frame)
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
        Tooltip(self.proceed_btn, "Continue to Summary & Export screen")
    
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
