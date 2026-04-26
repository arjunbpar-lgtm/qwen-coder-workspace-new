# ui/tooltip.py
import tkinter as tk
from tkinter import ttk


class Tooltip:
    """
    Create a tooltip for a given widget.
    
    The tooltip appears when the mouse hovers over the widget and disappears
    when the mouse leaves or the widget is clicked.
    
    Usage:
        widget = ttk.Button(parent, text="Help")
        Tooltip(widget, "This is helpful information")
    
    Or use the convenience function:
        from ui.tooltip import add_tooltip
        add_tooltip(widget, "Helpful text")
    """
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)
        self.widget.bind('<ButtonPress>', self.hide_tip)
    
    def show_tip(self, event=None):
        """Display the tooltip."""
        if self.tipwindow or not self.text:
            return
        
        # Get widget position
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Style the tooltip
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tkDefaultFont", "10", "normal"),
            wraplength=300
        )
        label.pack(ipadx=4, ipady=2)
    
    def hide_tip(self, event=None):
        """Hide the tooltip."""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def add_tooltip(widget, text):
    """
    Convenience function to add a tooltip to a widget.
    
    Args:
        widget: The Tkinter/ttk widget to attach the tooltip to
        text: The tooltip text to display
    """
    if text:
        Tooltip(widget, text)