# ui/help_panel.py
import tkinter as tk
from tkinter import ttk


class HelpPanel(ttk.Frame):
    """
    A reusable collapsible help panel component.
    
    Displays contextual help information with:
    - A toggle button to show/hide the panel
    - Purpose section explaining the screen's goal
    - Instructions section with step-by-step guidance
    - Key Rules section highlighting important constraints
    
    Usage:
        help_panel = HelpPanel(parent_frame)
        help_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        help_panel.set_content(
            purpose="Enter annual sales figures",
            instructions=["Step 1: Enter total sales", "Step 2: Select mode"],
            key_rules=["Sales must be positive", "Mode selection is required"]
        )
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.is_visible = False
        self.content_frame = None
        
        # Create toggle button with help icon
        self.toggle_btn = ttk.Button(
            self,
            text="❓ Help",
            command=self.toggle_visibility,
            width=8
        )
        self.toggle_btn.pack(anchor=tk.NE)
        
        # Initial state: hidden
        self._hide_content()
    
    def set_content(self, purpose="", instructions=None, key_rules=None):
        """
        Set the help content.
        
        Args:
            purpose: Brief description of the screen's purpose
            instructions: List of step-by-step instructions
            key_rules: List of important rules or constraints
        """
        # Destroy existing content if any
        if self.content_frame:
            self.content_frame.destroy()
        
        # Create new content frame
        self.content_frame = ttk.LabelFrame(self, text="Help & Guidance", padding=10)
        
        # Purpose section
        if purpose:
            purpose_label = ttk.Label(
                self.content_frame,
                text="Purpose:",
                font=("tkDefaultFont", 10, "bold")
            )
            purpose_label.pack(anchor=tk.W, pady=(0, 5))
            
            purpose_text = ttk.Label(
                self.content_frame,
                text=purpose,
                wraplength=250,
                justify=tk.LEFT
            )
            purpose_text.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))
        
        # Instructions section
        if instructions:
            instr_label = ttk.Label(
                self.content_frame,
                text="What to do:",
                font=("tkDefaultFont", 10, "bold")
            )
            instr_label.pack(anchor=tk.W, pady=(0, 5))
            
            for instruction in instructions:
                instr_text = ttk.Label(
                    self.content_frame,
                    text=f"• {instruction}",
                    wraplength=250,
                    justify=tk.LEFT
                )
                instr_text.pack(anchor=tk.W, fill=tk.X, pady=1)
            
            if key_rules:  # Add spacing before rules if both exist
                ttk.Separator(self.content_frame, orient=tk.HORIZONTAL).pack(
                    fill=tk.X, pady=10
                )
        
        # Key Rules section
        if key_rules:
            rules_label = ttk.Label(
                self.content_frame,
                text="Key Rules:",
                font=("tkDefaultFont", 10, "bold"),
                foreground="#d32f2f"
            )
            rules_label.pack(anchor=tk.W, pady=(0, 5))
            
            for rule in key_rules:
                rule_text = ttk.Label(
                    self.content_frame,
                    text=f"⚠ {rule}",
                    wraplength=250,
                    justify=tk.LEFT,
                    foreground="#d32f2f"
                )
                rule_text.pack(anchor=tk.W, fill=tk.X, pady=1)
        
        # Only pack if currently visible
        if self.is_visible:
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    
    def toggle_visibility(self):
        """Show or hide the help panel content."""
        if self.is_visible:
            self._hide_content()
        else:
            self._show_content()
    
    def _show_content(self):
        """Display the help content."""
        if self.content_frame:
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.is_visible = True
        self.toggle_btn.config(text="❌ Hide")
    
    def _hide_content(self):
        """Hide the help content."""
        if self.content_frame:
            self.content_frame.pack_forget()
        self.is_visible = False
        self.toggle_btn.config(text="❓ Help")
    
    def show(self):
        """Programmatically show the help panel."""
        if not self.is_visible:
            self._show_content()
    
    def hide(self):
        """Programmatically hide the help panel."""
        if self.is_visible:
            self._hide_content()