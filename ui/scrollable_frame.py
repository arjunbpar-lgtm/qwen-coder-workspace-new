# ui/scrollable_frame.py
import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    """
    A reusable scrollable frame component for Tkinter applications.
    
    This creates a canvas-based scrollable container that supports:
    - Vertical scrolling (always)
    - Horizontal scrolling (when content exceeds width)
    - Mouse wheel support
    - Automatic scrollbar appearance/disappearance
    - Responsive resizing
    
    Usage:
        parent = SomeWindow()
        scroll_frame = ScrollableFrame(parent)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add widgets to scroll_frame.container (NOT to scroll_frame directly)
        ttk.Label(scroll_frame.container, text="Content").pack()
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid weights for responsiveness
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create canvas
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Create vertical scrollbar
        self.vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.vsb.grid(row=0, column=1, sticky=tk.NS)
        
        # Create horizontal scrollbar
        self.hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.hsb.grid(row=1, column=0, sticky=tk.EW)
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        
        # Create the inner frame that will hold actual content
        self.container = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.container, anchor=tk.NW)
        
        # Bind events for proper scrolling behavior
        self.container.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Bind mouse wheel scrolling
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Button-4>', self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all('<Button-5>', self._on_mousewheel)  # Linux scroll down
        
        # Track if we're currently updating scroll region to avoid recursion
        self._updating_scroll_region = False
    
    def _on_frame_configure(self, event=None):
        """Update the scroll region when the inner frame changes size."""
        if not self._updating_scroll_region:
            self._updating_scroll_region = True
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
            self._updating_scroll_region = False
    
    def _on_canvas_configure(self, event=None):
        """Resize the inner frame to match canvas width (optional behavior)."""
        # Only adjust width if you want the content to fill the canvas width
        # Uncomment the following line if you want automatic width adjustment:
        # self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        # Update scroll region in case canvas resize affects visibility
        self.after_idle(self._on_frame_configure)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, 'units')
    
    def scroll_to_top(self):
        """Scroll to the top of the content."""
        self.canvas.yview_moveto(0)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the content."""
        self.canvas.yview_moveto(1)
    
    def update_idletasks(self):
        """Override to ensure container updates are processed."""
        super().update_idletasks()
        self.canvas.update_idletasks()