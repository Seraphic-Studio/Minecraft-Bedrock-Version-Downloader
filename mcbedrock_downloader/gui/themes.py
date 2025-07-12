from typing import Dict, Any


LIGHT_COLORS = {
    'bg': '#f3f3f3',
    'surface': '#ffffff',
    'surface_variant': '#f9f9f9',
    'primary': '#0078d4',
    'primary_dark': '#005a9e',
    'primary_light': '#40e0ff',
    'secondary': '#6b6b6b',
    'accent': '#0099bc',
    'text': '#323130',
    'text_secondary': '#605e5c',
    'border': '#e1dfdd',
    'hover': '#f5f5f5',
    'success': '#107c10',
    'error': '#d13438',
    'warning': '#ffa500',
    'card_shadow': '#00000010'
}

DARK_COLORS = {
    'bg': '#1f1f1f',
    'surface': '#2d2d2d',
    'surface_variant': '#3a3a3a',
    'primary': '#60cdff',
    'primary_dark': '#0078d4',
    'primary_light': '#40e0ff',
    'secondary': '#8a8a8a',
    'accent': '#60cdff',
    'text': '#ffffff',
    'text_secondary': '#cccccc',
    'border': '#404040',
    'hover': '#3f3f3f',
    'success': '#6ccb5f',
    'error': '#ff6b6b',
    'warning': '#ffb347',
    'card_shadow': '#00000030'
}


class ThemeManager:
    
    def __init__(self):
        self.current_theme = 'light'
        self.themes = {
            'light': LIGHT_COLORS,
            'dark': DARK_COLORS
        }
        
    def get_colors(self, theme: str = None) -> Dict[str, str]:
        """Get colors for the specified theme"""
        if theme is None:
            theme = self.current_theme
        return self.themes.get(theme, LIGHT_COLORS)
        
    def set_theme(self, theme: str):
        """Set the current theme"""
        if theme in self.themes:
            self.current_theme = theme
            
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        
    def get_current_colors(self) -> Dict[str, str]:
        """Get colors for the current theme"""
        return self.get_colors(self.current_theme)
        
    def is_dark_theme(self) -> bool:
        """Check if current theme is dark"""
        return self.current_theme == 'dark'
