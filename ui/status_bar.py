import tkinter as tk
from tkinter import ttk


class StatusBar(ttk.Frame):
    """
    A reusable status bar component for displaying validation feedback and messages.
    
    Features:
    - Color-coded status indicators (green for valid, red for errors, orange for warnings)
    - Multi-line message support
    - Auto-hide when no message
    - Responsive width
    
    Usage:
        status_bar = StatusBar(parent_frame)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set status
        status_bar.set_status("Valid", "All inputs are correct")
        status_bar.set_error("Invalid", "Total percentage is 105%")
        status_bar.clear()
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure style
        self.configure(relief=tk.RAISED, borderwidth=1)
        
        # Status label (left side)
        self.status_label = ttk.Label(
            self,
            text="Ready",
            font=("tkDefaultFont", 10, "bold"),
            padding=(10, 5)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.Y)
        
        # Message label (right side, expandable)
        self.message_label = ttk.Label(
            self,
            text="",
            font=("tkDefaultFont", 10),
            padding=(5, 5)
        )
        self.message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize state
        self._current_state = "normal"
    
    def set_status(self, status_text, message_text="", state="normal"):
        """
        Set the status bar content with optional color coding.
        
        Args:
            status_text: Short status indicator (e.g., "Valid", "Error")
            message_text: Detailed message
            state: "valid", "error", "warning", or "normal"
        """
        self.status_label.config(text=status_text)
        self.message_label.config(text=message_text)
        
        # Apply color based on state
        if state == "valid":
            self.status_label.configure(foreground="#2e7d32")  # Green
            self.message_label.configure(foreground="#2e7d32")
        elif state == "error":
            self.status_label.configure(foreground="#c62828")  # Red
            self.message_label.configure(foreground="#c62828")
        elif state == "warning":
            self.status_label.configure(foreground="#f57c00")  # Orange
            self.message_label.configure(foreground="#f57c00")
        else:
            self.status_label.configure(foreground="black")
            self.message_label.configure(foreground="black")
        
        self._current_state = state
    
    def set_valid(self, message=""):
        """Set status to valid (green)."""
        self.set_status("✓ Valid", message, state="valid")
    
    def set_error(self, message=""):
        """Set status to error (red)."""
        self.set_status("✗ Error", message, state="error")
    
    def set_warning(self, message=""):
        """Set status to warning (orange)."""
        self.set_status("⚠ Warning", message, state="warning")
    
    def clear(self):
        """Clear the status bar."""
        self.status_label.config(text="Ready", foreground="black")
        self.message_label.config(text="", foreground="black")
        self._current_state = "normal"
    
    def get_state(self):
        """Get current state."""
        return self._current_state