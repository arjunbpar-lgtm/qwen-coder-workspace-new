"""
Tooltip utility for Tkinter/ttk widgets.

Provides a lightweight tooltip implementation that appears on hover.
"""

import tkinter as tk
from tkinter import ttk


class Tooltip:
    """
    Create a tooltip for a given widget.
    
    The tooltip appears when the mouse hovers over the widget
    and disappears when the mouse leaves or after a timeout.
    
    Usage:
        widget = ttk.Button(parent, text="Click me")
        Tooltip(widget, "This is a helpful tooltip")
    """
    
    def __init__(self, widget, text):
        """
        Initialize tooltip for a widget.
        
        Args:
            widget: The Tkinter/ttk widget to attach tooltip to
            text: The tooltip text to display
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.after_id = None
        
        # Bind events
        self.widget.bind('<Enter>', self._on_enter)
        self.widget.bind('<Leave>', self._on_leave)
        self.widget.bind('<ButtonPress>', self._on_leave)
    
    def _on_enter(self, event=None):
        """Handle mouse enter event - show tooltip after delay."""
        self.after_id = self.widget.after(500, self._show_tooltip)
    
    def _on_leave(self, event=None):
        """Handle mouse leave event - hide tooltip."""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self._hide_tooltip()
    
    def _show_tooltip(self):
        """Create and display the tooltip window."""
        if self.tooltip_window is not None:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        
        # Remove window decorations
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Create label with tooltip text
        label = ttk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            padding=(5, 3),
            font=('Helvetica', 9)
        )
        label.pack(ipadx=3, ipady=3)
        
        # Make sure tooltip stays on top
        tw.wm_attributes("-topmost", True)
    
    def _hide_tooltip(self):
        """Hide and destroy the tooltip window."""
        if self.tooltip_window is not None:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def configure(self, text=None):
        """
        Update tooltip configuration.
        
        Args:
            text: New tooltip text (optional)
        """
        if text is not None:
            self.text = text


def add_tooltip(widget, text):
    """
    Convenience function to add a tooltip to a widget.
    
    Args:
        widget: The widget to attach tooltip to
        text: The tooltip text
    
    Returns:
        Tooltip instance
    """
    return Tooltip(widget, text)
