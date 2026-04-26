"""
System Log Screen.

Screen for viewing and managing application logs.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class SystemLogScreen(ttk.Frame):
    """
    Screen for viewing system logs.
    
    Features:
    - Display live logs in scrolling text box
    - Copy Log button
    - Export Log button
    - Clear Log button
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
            text="System Log",
            font=('Helvetica', 16, 'bold')
        ).grid(row=0, column=0)
        
        ttk.Label(
            title_frame,
            text="View application logs and events",
            font=('Helvetica', 10)
        ).grid(row=1, column=0, pady=5)
        
        # Content frame
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Log display with scrollbar
        log_frame = ttk.LabelFrame(content_frame, text="Application Logs", padding="10")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            font=('Courier', 9),
            state=tk.DISABLED,
            bg='#f5f5f5'
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, pady=20)
        
        self.copy_btn = ttk.Button(
            button_frame,
            text="Copy Log",
            command=self.copy_log,
            width=15
        )
        self.copy_btn.grid(row=0, column=0, padx=10)
        
        self.export_btn = ttk.Button(
            button_frame,
            text="Export Log",
            command=self.export_log,
            width=15
        )
        self.export_btn.grid(row=0, column=1, padx=10)
        
        self.clear_btn = ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log,
            width=15
        )
        self.clear_btn.grid(row=0, column=2, padx=10)
        
        self.back_btn = ttk.Button(
            button_frame,
            text="← Back",
            command=self.go_back,
            width=15
        )
        self.back_btn.grid(row=0, column=3, padx=10)
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        self.refresh_check = ttk.Checkbutton(
            self,
            text="Auto-refresh",
            variable=self.auto_refresh_var
        )
        self.refresh_check.grid(row=3, column=0, pady=5)
    
    def load_logs(self):
        """Load logs from the logger and display."""
        logger = self.controller.get_logger()
        if logger:
            logs = logger.get_logs(limit=500)
            
            # Update display
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete('1.0', tk.END)
            
            for log_entry in logs:
                self.log_text.insert(tk.END, log_entry + '\n')
            
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)
    
    def copy_log(self):
        """Copy log contents to clipboard."""
        try:
            logs = self.log_text.get('1.0', tk.END)
            self.clipboard_clear()
            self.clipboard_append(logs)
            messagebox.showinfo("Copied", "Log contents copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy log: {e}")
    
    def export_log(self):
        """Export log to file."""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Log File"
            )
            
            if filepath:
                logs = self.log_text.get('1.0', tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(logs)
                
                messagebox.showinfo(
                    "Export Successful",
                    f"Log exported successfully!\n\nFile: {filepath}"
                )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export log: {e}")
    
    def clear_log(self):
        """Clear the log display."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the log display?"):
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete('1.0', tk.END)
            self.log_text.configure(state=tk.DISABLED)
            
            # Also clear the logger buffer
            logger = self.controller.get_logger()
            if logger:
                logger.clear_logs()
    
    def go_back(self):
        """Go back to main menu."""
        self.controller.show_screen("sales_input")
