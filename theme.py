# theme.py
"""
Modern Theme System for FocusSuite
===================================
Beautiful, modern color scheme based on the app icon's blue gradient (#2563eb to #06b6d4)
"""

class ModernTheme:
    """Modern color palette for FocusSuite - Based on app icon"""
    
    # Brand colors from icon (Blue gradient)
    PRIMARY_BLUE = "#2563eb"     # Royal Blue (left side of icon)
    SECONDARY_BLUE = "#06b6d4"   # Cyan (right side of icon)
    ACCENT_BLUE = "#3b82f6"      # Medium Blue
    LIGHT_BLUE = "#60a5fa"       # Sky Blue
    
    # Status colors (universal)
    SUCCESS = "#10b981"      # Green
    WARNING = "#f59e0b"      # Amber
    DANGER = "#ef4444"       # Red
    INFO = "#3b82f6"         # Blue
    
    # Gamification colors
    XP_COLOR = "#fbbf24"         # Amber 400
    LEVEL_COLOR = "#a78bfa"      # Violet 400
    STREAK_COLOR = "#fb923c"     # Orange 400
    ACHIEVEMENT_COLOR = "#fcd34d"  # Amber 300
    
    @classmethod
    def get_bg(cls):
        """Get background color"""
        return "#ffffff"
    
    @classmethod
    def get_bg_secondary(cls):
        """Get secondary background color"""
        return "#f8fafc"
    
    @classmethod
    def get_text(cls):
        """Get primary text color"""
        return "#0f172a"
    
    @classmethod
    def get_text_secondary(cls):
        """Get secondary text color"""
        return "#475569"
    
    @classmethod
    def get_border(cls):
        """Get border color"""
        return "#e2e8f0"
    
    @classmethod
    def get_input_bg(cls):
        """Get input field background"""
        return "#ffffff"
    
    @classmethod
    def get_card_bg(cls):
        """Get card background"""
        return "#ffffff"
    
    @staticmethod
    def get_priority_color(priority):
        """Get color based on task priority"""
        colors = {
            'Critical': ModernTheme.DANGER,
            'High': ModernTheme.WARNING,
            'Normal': ModernTheme.ACCENT_BLUE,
            'Low': "#94a3b8"  # Slate 400
        }
        return colors.get(priority, ModernTheme.ACCENT_BLUE)
    
    @staticmethod
    def get_status_color(status):
        """Get color based on task status"""
        colors = {
            'Done': ModernTheme.SUCCESS,
            'Pending': ModernTheme.WARNING,
            'Overdue': ModernTheme.DANGER
        }
        return colors.get(status, "#94a3b8")


class ThemeManager:
    """
    Manages theme application to tkinter widgets
    """
    
    @staticmethod
    def configure_style(style):
        """Configure ttk.Style with modern theme"""
        theme = ModernTheme
        
        # Configure Notebook (tabs) - Fixed width, no shrinking
        style.configure('TNotebook', 
                       background=theme.get_bg(), 
                       borderwidth=0,
                       tabmargins=[10, 10, 10, 0])
        
        style.configure('TNotebook.Tab', 
                       background=theme.get_bg_secondary(),
                       foreground=theme.get_text_secondary(),
                       padding=[25, 12],  # Wider padding
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('TNotebook.Tab',
                 background=[('selected', theme.PRIMARY_BLUE)],
                 foreground=[('selected', '#ffffff')])
        
        # Configure Frames
        style.configure('TFrame', background=theme.get_bg())
        style.configure('Card.TFrame', 
                       background=theme.get_card_bg(), 
                       relief='flat')
        
        # Configure Labels
        style.configure('TLabel', 
                       background=theme.get_bg(),
                       foreground=theme.get_text(),
                       font=('Segoe UI', 10))
        
        style.configure('Title.TLabel',
                       font=('Segoe UI', 16, 'bold'),
                       foreground=theme.get_text())
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 12),
                       foreground=theme.get_text_secondary())
        
        style.configure('Stat.TLabel',
                       font=('Segoe UI', 24, 'bold'),
                       foreground=theme.PRIMARY_BLUE)
        
        # Configure Buttons
        style.configure('TButton',
                       background=theme.PRIMARY_BLUE,
                       foreground='#ffffff',
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('TButton',
                 background=[('active', theme.ACCENT_BLUE), 
                           ('pressed', theme.SECONDARY_BLUE)])
        
        style.configure('Accent.TButton',
                       background=theme.SECONDARY_BLUE,
                       foreground='#ffffff')
        
        style.map('Accent.TButton',
                 background=[('active', theme.ACCENT_BLUE)])
        
        style.configure('Success.TButton',
                       background=theme.SUCCESS,
                       foreground='#ffffff')
        
        style.configure('Danger.TButton',
                       background=theme.DANGER,
                       foreground='#ffffff')
        
        style.configure('Warning.TButton',
                       background=theme.WARNING,
                       foreground='#ffffff')
        
        # Configure Entry
        style.configure('TEntry',
                       fieldbackground=theme.get_input_bg(),
                       foreground=theme.get_text(),
                       borderwidth=1,
                       bordercolor=theme.get_border(),
                       insertcolor=theme.get_text())
        
        # Configure Treeview
        style.configure('Treeview',
                       background=theme.get_card_bg(),
                       foreground=theme.get_text(),
                       fieldbackground=theme.get_card_bg(),
                       borderwidth=0,
                       rowheight=35)
        
        style.configure('Treeview.Heading',
                       background='#64748b',
                       foreground='#ffffff',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Treeview',
                 background=[('selected', theme.PRIMARY_BLUE)],
                 foreground=[('selected', '#ffffff')])
        
        # Configure Progressbar
        style.configure('TProgressbar',
                       background=theme.PRIMARY_BLUE,
                       troughcolor=theme.get_bg_secondary(),
                       borderwidth=0,
                       thickness=20)
        
        # Configure Combobox
        style.configure('TCombobox',
                       fieldbackground=theme.get_input_bg(),
                       background=theme.get_input_bg(),
                       foreground=theme.get_text(),
                       arrowcolor=theme.get_text(),
                       borderwidth=1,
                       bordercolor=theme.get_border())
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', theme.get_input_bg())],
                 selectbackground=[('readonly', theme.get_input_bg())],
                 selectforeground=[('readonly', theme.get_text())])
    
    @staticmethod
    def create_card_frame(parent, **kwargs):
        """Create a card-style frame with modern styling"""
        import tkinter as tk
        theme = ModernTheme
        frame = tk.Frame(parent, 
                        bg=theme.get_card_bg(),
                        highlightbackground=theme.get_border(),
                        highlightthickness=1,
                        **kwargs)
        return frame
    
    @staticmethod
    def create_gradient_label(parent, text, **kwargs):
        """Create a label with gradient-like appearance"""
        import tkinter as tk
        theme = ModernTheme
        label = tk.Label(parent,
                        text=text,
                        bg=theme.get_card_bg(),
                        fg=theme.PRIMARY_BLUE,
                        font=('Segoe UI', 12, 'bold'),
                        **kwargs)
        return label
    
    @staticmethod
    def create_icon_button(parent, text, command, style='TButton', **kwargs):
        """Create a modern button with icon support"""
        from tkinter import ttk
        btn = ttk.Button(parent, text=text, command=command, style=style, **kwargs)
        return btn


# Export theme instance
theme = ModernTheme()
theme_manager = ThemeManager()
