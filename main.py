"""
Sales Ledger Generator - Main Application (Multi-Screen Version)

A desktop utility for accountants to generate realistic yearly sales
ledger entries and export them to Excel and TallyPrime XML format.

This version uses a multi-screen wizard structure with frame-based navigation.

Usage:
    python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from typing import Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_controller import AppController
from utils.logger import get_logger

# Import screens
from screens.screen_sales_input import SalesInputScreen
from screens.screen_month_distribution import MonthlyDistributionScreen
from screens.screen_month_generator import MonthGeneratorScreen
from screens.screen_preview import PreviewScreen
from screens.screen_summary import SummaryScreen
from screens.screen_cash_split import CashSplitScreen
from screens.screen_system_log import SystemLogScreen


class SalesLedgerApp:
    """
    Main Tkinter application with multi-screen wizard structure.
    
    Manages frame-based screen switching for:
    - Sales Input Screen
    - Monthly Distribution Screen
    - Month Generator Screen
    - Preview Screen
    - Summary / Export Screen
    - Cash Split Utility Screen
    - System Log Screen
    """
    
    def __init__(self, root):
        """
        Initialize the application window and screen system.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Sales Ledger Generator")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Initialize controller
        self.controller = AppController(root)
        self.logger = get_logger()
        
        # Container for all frames
        self.container = ttk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Store all screens
        self.frames = {}
        
        # Setup all screens
        self._setup_screens()
        
        # Show initial screen
        self.show_screen("sales_input")
        
        # Configure grid
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        
        # Menu bar
        self._create_menu()
        
        self.logger.info("Application started")
    
    def _create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Cash Split Utility", 
                               command=lambda: self.show_screen("cash_split"))
        tools_menu.add_command(label="System Log", 
                               command=lambda: self.show_screen("system_log"))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _setup_screens(self):
        """Initialize all screen frames."""
        screen_classes = {
            "sales_input": SalesInputScreen,
            "monthly_distribution": MonthlyDistributionScreen,
            "month_generator": MonthGeneratorScreen,
            "preview": PreviewScreen,
            "summary": SummaryScreen,
            "cash_split": CashSplitScreen,
            "system_log": SystemLogScreen
        }
        
        for name, screen_class in screen_classes.items():
            frame = screen_class(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def show_screen(self, screen_name):
        """
        Switch to the specified screen.
        
        Args:
            screen_name: Name of the screen to show
        """
        if screen_name in self.frames:
            # Hide all frames
            for frame in self.frames.values():
                frame.grid_remove()
            
            # Show requested frame
            self.frames[screen_name].grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Load data for specific screens
            if screen_name == "month_generator":
                self.frames[screen_name].load_month_data()
            elif screen_name == "preview":
                self.frames[screen_name].load_entries()
            elif screen_name == "summary":
                self.frames[screen_name].load_statistics()
            elif screen_name == "system_log":
                self.frames[screen_name].load_logs()
            
            self.logger.debug(f"Switched to screen: {screen_name}")

    def __getattr__(self, name: str) -> Any:
        """
        Proxy controller methods for screens.

        Screens receive the app instance so they can navigate with
        ``show_screen()``. Most of their data operations live on the
        AppController, so unknown attributes are delegated there.
        """
        return getattr(self.controller, name)
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Sales Ledger Generator\n\n"
            "A multi-screen accounting tool for generating\n"
            "realistic sales ledger entries.\n\n"
            "Features:\n"
            "- Annual sales distribution\n"
            "- Monthly breakdown\n"
            "- Daily entry generation\n"
            "- Tally XML export\n"
            "- Excel export\n"
            "- Cash split utility"
        )


def main():
    """Main entry point."""
    root = tk.Tk()
    app = SalesLedgerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
