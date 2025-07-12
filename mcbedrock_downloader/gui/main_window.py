"""
Main GUI window for Minecraft Bedrock Version Downloader
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import asyncio
import threading
import json
import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Callable
import webbrowser

from mcbedrock_downloader.gui.downloader import VersionDownloader, VersionList, BadUpdateIdentityException, format_size

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

COLORS = LIGHT_COLORS
class DownloaderGUI:
    """Main GUI class for Minecraft Bedrock Version Downloader"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Bedrock Version Downloader")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        self.dark_mode = tk.BooleanVar(value=False)
        
        self.root.configure(bg=COLORS['bg'])
        
        self.style = ttk.Style()
        self.configure_modern_style()
        
        self.version_list = None
        self.current_download = None
        self.download_thread = None
        self.download_task = None  
        self.download_cancelled = False
        self.msa_token = tk.StringVar()
        self.selected_version = None
        self.output_path = tk.StringVar()
        self.version_filter = tk.StringVar(value="all")
        self.search_query = tk.StringVar()  
        self.progress_var = tk.DoubleVar()
        self.download_status = tk.StringVar(value="Ready")
        self.versions_data = []
        
        self.create_widgets()
        self.create_menu()
        
        self.load_versions()
        
    def configure_modern_style(self):
        """Configure modern Windows 11-like styling"""
        self.style.theme_use('clam')
        
        self.style.configure('Modern.TFrame', 
                           background=COLORS['surface'], 
                           relief='flat', 
                           borderwidth=0)
        
        self.style.configure('Card.TFrame', 
                           background=COLORS['surface'], 
                           relief='flat', 
                           borderwidth=1,
                           fieldbackground=COLORS['surface'])
        
        self.style.configure('Sidebar.TFrame', 
                           background=COLORS['surface_variant'])
        
        self.style.configure('Title.TLabel', 
                           background=COLORS['bg'], 
                           foreground=COLORS['text'],
                           font=('Segoe UI', 24, 'normal'))
        
        self.style.configure('Heading.TLabel', 
                           background=COLORS['surface'], 
                           foreground=COLORS['text'],
                           font=('Segoe UI', 12, 'bold'))
        
        self.style.configure('Modern.TLabel', 
                           background=COLORS['surface'], 
                           foreground=COLORS['text'],
                           font=('Segoe UI', 9))
        
        self.style.configure('Status.TLabel', 
                           background=COLORS['surface'], 
                           foreground=COLORS['text_secondary'],
                           font=('Segoe UI', 9))
        
        self.style.configure('Modern.TButton',
                           background=COLORS['primary'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           relief='flat',
                           padding=(20, 10),
                           font=('Segoe UI', 9, 'normal'))
        
        self.style.map('Modern.TButton',
                      background=[('active', COLORS['primary_dark']),
                                ('pressed', COLORS['primary_dark']),
                                ('disabled', COLORS['border'])],
                      foreground=[('disabled', COLORS['text_secondary'])])
        
        self.style.configure('Secondary.TButton',
                           background=COLORS['surface'],
                           foreground=COLORS['text'],
                           borderwidth=1,
                           focuscolor='none',
                           relief='flat',
                           padding=(20, 10),
                           font=('Segoe UI', 9, 'normal'))
        
        self.style.map('Secondary.TButton',
                      background=[('active', COLORS['hover']),
                                ('pressed', COLORS['hover']),
                                ('disabled', COLORS['surface'])],
                      foreground=[('disabled', COLORS['text_secondary'])],
                      bordercolor=[('focus', COLORS['border']),
                                 ('!focus', COLORS['border'])])
        
        self.style.configure('Toggle.TButton',
                           background=COLORS['surface_variant'],
                           foreground=COLORS['text'],
                           borderwidth=1,
                           focuscolor='none',
                           relief='flat',
                           padding=(10, 5),
                           font=('Segoe UI', 9))
        
        self.style.map('Toggle.TButton',
                      background=[('active', COLORS['hover']),
                                ('pressed', COLORS['hover'])],
                      bordercolor=[('focus', COLORS['border']),
                                 ('!focus', COLORS['border'])])
        
        self.style.configure('Modern.TEntry',
                           fieldbackground=COLORS['surface'],
                           foreground=COLORS['text'],
                           borderwidth=1,
                           relief='flat',
                           padding=(10, 8),
                           font=('Segoe UI', 9))
        
        self.style.map('Modern.TEntry',
                      bordercolor=[('focus', COLORS['border']),
                                 ('!focus', COLORS['border'])])
        
        self.style.configure('Modern.TCombobox',
                           fieldbackground=COLORS['surface'],
                           foreground=COLORS['text'],
                           borderwidth=1,
                           relief='flat',
                           padding=(10, 8),
                           font=('Segoe UI', 9))
        
        self.style.map('Modern.TCombobox',
                      bordercolor=[('focus', COLORS['border']),
                                 ('!focus', COLORS['border'])])
        
        self.style.configure('Modern.Horizontal.TProgressbar',
                           background=COLORS['primary'],
                           troughcolor=COLORS['border'],
                           borderwidth=0,
                           lightcolor=COLORS['primary'],
                           darkcolor=COLORS['primary'],
                           relief='flat')
        
        self.style.configure('Modern.Treeview',
                           background=COLORS['surface'],
                           foreground=COLORS['text'],
                           fieldbackground=COLORS['surface'],
                           borderwidth=1,
                           relief='flat',
                           font=('Segoe UI', 9))
        
        self.style.configure('Modern.Treeview.Heading',
                           background=COLORS['surface_variant'],
                           foreground=COLORS['text'],
                           relief='flat',
                           borderwidth=0,
                           padding=(10, 8),
                           font=('Segoe UI', 9, 'bold'))
        
        self.style.map('Modern.Treeview',
                      background=[('selected', COLORS['surface'])],
                      foreground=[('selected', COLORS['text'])])
        
        self.style.map('Modern.Treeview.Heading',
                      background=[('active', COLORS['hover'])])
        
        self.style.configure('Modern.TLabelframe',
                           background=COLORS['surface'],
                           borderwidth=1,
                           relief='flat')
        
        self.style.configure('Modern.TLabelframe.Label',
                           background=COLORS['surface'],
                           foreground=COLORS['text'],
                           font=('Segoe UI', 10, 'bold'))
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh Version List", command=self.load_versions)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Open Download Folder", command=self.open_download_folder)
        tools_menu.add_command(label="Clear Log", command=self.clear_log)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Get MSA Token", command=self.show_token_help)
        
    def create_widgets(self):
        """Create main GUI widgets with Windows 11 styling"""
        main_container = tk.Frame(self.root, bg=COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(main_container, bg=COLORS['bg'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg=COLORS['bg'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = ttk.Label(title_frame, text="Minecraft Bedrock", 
                               style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Version Downloader", 
                                  style='Heading.TLabel', foreground=COLORS['text_secondary'])
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))
        
        controls_frame = tk.Frame(header_frame, bg=COLORS['bg'])
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dark_mode_btn = ttk.Button(controls_frame, text="🌙 Dark", 
                                       command=self.toggle_dark_mode,
                                       style='Toggle.TButton')
        self.dark_mode_btn.pack(anchor=tk.E, pady=(10, 0))
        
        content_frame = tk.Frame(main_container, bg=COLORS['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = self.create_card_frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        self.create_version_card(left_panel)
        
        right_panel = tk.Frame(content_frame, bg=COLORS['bg'], width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self.create_config_card(right_panel)
        
        self.create_progress_card(right_panel)
        
        self.create_log_card(right_panel)
    
    def create_card_frame(self, parent):
        """Create a Windows 11 style card frame"""
        card = tk.Frame(parent, bg=COLORS['surface'], relief='flat', bd=1)
        card.configure(highlightbackground=COLORS['surface'], highlightthickness=0)
        return card
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self.create_config_card(right_panel)
        
        self.create_progress_card(right_panel)
        
        self.create_log_card(right_panel)
        
    def create_version_card(self, parent):
        """Create version selection card with Windows 11 styling"""
        card = tk.Frame(parent, bg=COLORS['surface'], padx=25, pady=25)
        card.pack(fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(card, bg=COLORS['surface'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Available Versions", 
                               style='Heading.TLabel')
        title_label.pack(side=tk.LEFT)
        
        controls_frame = tk.Frame(card, bg=COLORS['surface'])
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        search_label = ttk.Label(controls_frame, text="Search:", style='Modern.TLabel')
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        search_entry = ttk.Entry(controls_frame, textvariable=self.search_query, 
                                width=20, style='Modern.TEntry')
        search_entry.pack(side=tk.LEFT, padx=(0, 15))
        search_entry.bind('<KeyRelease>', self.filter_versions)
        
        filter_label = ttk.Label(controls_frame, text="Filter:", style='Modern.TLabel')
        filter_label.pack(side=tk.LEFT, padx=(0, 10))
        
        filter_combo = ttk.Combobox(controls_frame, textvariable=self.version_filter, 
                                   values=["all", "release", "beta", "preview"], 
                                   state="readonly", width=12, style='Modern.TCombobox')
        filter_combo.pack(side=tk.LEFT, padx=(0, 15))
        filter_combo.bind('<<ComboboxSelected>>', self.filter_versions)
        
        refresh_btn = ttk.Button(controls_frame, text="Refresh", 
                                command=self.load_versions,
                                style='Secondary.TButton')
        refresh_btn.pack(side=tk.RIGHT)
        
        list_frame = tk.Frame(card, bg=COLORS['surface'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Name', 'Type', 'UUID')
        self.version_tree = ttk.Treeview(list_frame, columns=columns, show='headings', 
                                        style='Modern.Treeview')
        
        self.version_tree.heading('Name', text='Version Name')
        self.version_tree.heading('Type', text='Type')
        self.version_tree.heading('UUID', text='UUID')
        
        self.version_tree.column('Name', width=180, anchor=tk.W)
        self.version_tree.column('Type', width=80, anchor=tk.CENTER)
        self.version_tree.column('UUID', width=280, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.version_tree.yview)
        self.version_tree.configure(yscrollcommand=scrollbar.set)
        
        self.version_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.version_tree.bind('<<TreeviewSelect>>', self.on_version_select)
        
    def create_config_card(self, parent):
        """Create configuration card with Windows 11 styling"""
        card = self.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        content = tk.Frame(card, bg=COLORS['surface'], padx=25, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(content, text="Download Configuration", 
                               style='Heading.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        path_label = ttk.Label(content, text="Output Path:", style='Modern.TLabel')
        path_label.pack(anchor=tk.W, pady=(0, 8))
        
        path_frame = tk.Frame(content, bg=COLORS['surface'])
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.output_entry = ttk.Entry(path_frame, textvariable=self.output_path, 
                                     font=('Segoe UI', 9), style='Modern.TEntry')
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(path_frame, text="Browse", 
                               command=self.browse_output_path,
                               style='Secondary.TButton')
        browse_btn.pack(side=tk.RIGHT)
        
        token_label = ttk.Label(content, text="MSA Token (Optional for most versions):", 
                               style='Modern.TLabel')
        token_label.pack(anchor=tk.W, pady=(0, 8))
        
        token_frame = tk.Frame(content, bg=COLORS['surface'])
        token_frame.pack(fill=tk.X, pady=(0, 10))
        
        token_entry = ttk.Entry(token_frame, textvariable=self.msa_token, show="*", 
                               font=('Segoe UI', 9), style='Modern.TEntry')
        token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        token_help_btn = ttk.Button(token_frame, text="?", 
                                   command=self.show_token_help,
                                   style='Secondary.TButton', width=3)
        token_help_btn.pack(side=tk.RIGHT)
        
        explanation = ttk.Label(content, 
                               text="Most beta versions download without authentication. "
                                    "Token only required for exclusive insider builds.",
                               style='Status.TLabel', wraplength=320)
        explanation.pack(anchor=tk.W, pady=(0, 20))
        
    def create_progress_card(self, parent):
        """Create progress card with Windows 11 styling"""
        card = self.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        content = tk.Frame(card, bg=COLORS['surface'], padx=25, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(content, text="Download Progress", 
                               style='Heading.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        self.status_label = ttk.Label(content, textvariable=self.download_status, 
                                     style='Status.TLabel')
        self.status_label.pack(anchor=tk.W, pady=(0, 15))
        
        self.progress_bar = ttk.Progressbar(content, variable=self.progress_var, 
                                           maximum=100, style='Modern.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(0, 25))
        
        button_frame = tk.Frame(content, bg=COLORS['surface'])
        button_frame.pack(fill=tk.X)
        
        self.download_btn = ttk.Button(button_frame, text="Download Selected Version", 
                                      command=self.start_download, state=tk.DISABLED,
                                      style='Modern.TButton')
        self.download_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", 
                                    command=self.cancel_download, state=tk.DISABLED,
                                    style='Secondary.TButton')
        self.cancel_btn.pack(side=tk.LEFT)
        
    def create_log_card(self, parent):
        """Create log card with Windows 11 styling"""
        card = self.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True)
        
        content = tk.Frame(card, bg=COLORS['surface'], padx=25, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(content, bg=COLORS['surface'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Activity Log", 
                               style='Heading.TLabel')
        title_label.pack(side=tk.LEFT)
        
        clear_btn = ttk.Button(header_frame, text="Clear", 
                              command=self.clear_log,
                              style='Secondary.TButton')
        clear_btn.pack(side=tk.RIGHT)
        
        log_frame = tk.Frame(content, bg=COLORS['surface'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, 
                                                 font=('Consolas', 9),
                                                 bg=COLORS['surface'],
                                                 fg=COLORS['text'],
                                                 selectbackground=COLORS['surface'],
                                                 selectforeground=COLORS['text'],
                                                 wrap=tk.WORD,
                                                 relief='flat',
                                                 borderwidth=1,
                                                 highlightbackground=COLORS['surface'],
                                                 highlightthickness=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log_message(self, message: str):
        """Add message to log with modern styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete(1.0, f"{len(lines)-500}.0")
            
    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
        
    def load_versions(self):
        """Load version list from API"""
        def load_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                self.log_message("Loading version list...")
                self.download_status.set("Loading versions...")
                
                version_list = VersionList()
                
                loop.run_until_complete(version_list.download_list())
                
                self.root.after(0, self.update_version_list, version_list.versions)
                
            except Exception as e:
                self.root.after(0, self.show_error, f"Error loading versions: {str(e)}")
            finally:
                loop.close()
                
        thread = threading.Thread(target=load_async, daemon=True)
        thread.start()
        
    def update_version_list(self, versions: List[Dict]):
        """Update version list in GUI"""
        def version_key(v):
            try:
                parts = v['name'].split('.')
                return tuple(int(part) for part in parts)
            except:
                return v['name']
        
        sorted_versions = sorted(versions, key=version_key, reverse=True)
        self.versions_data = sorted_versions
        self.filter_versions()
        self.download_status.set("Ready")
        self.log_message(f"Loaded {len(versions)} versions")
        
    def filter_versions(self, event=None):
        """Filter versions based on selected filter and search query"""
        for item in self.version_tree.get_children():
            self.version_tree.delete(item)
            
        if not self.versions_data:
            return
            
        filter_value = self.version_filter.get()
        search_value = self.search_query.get().lower()
        
        for version in self.versions_data:
            if filter_value != "all" and version['type_name'].lower() != filter_value:
                continue
                
            if search_value:
                if (search_value not in version['name'].lower() and 
                    search_value not in version['uuid'].lower() and
                    search_value not in version['type_name'].lower()):
                    continue
                    
            self.version_tree.insert('', 'end', values=(
                version['name'],
                version['type_name'],
                version['uuid']
            ))
                
    def on_version_select(self, event):
        """Handle version selection"""
        selection = self.version_tree.selection()
        if selection:
            item = self.version_tree.item(selection[0])
            values = item['values']
            
            for version in self.versions_data:
                if version['uuid'] == values[2]:
                    self.selected_version = version
                    break
                    
            if self.selected_version:
                type_name = self.selected_version['type_name']
                version_name = self.selected_version['name']
                
                if type_name == "Preview":
                    filename = f"Minecraft-Preview-{version_name}.appx"
                else:
                    filename = f"Minecraft-{version_name}.appx"
                    
                self.output_path.set(filename)
                self.download_btn.config(state=tk.NORMAL)
                self.log_message(f"Selected version: {version_name} ({type_name})")
                
    def browse_output_path(self):
        """Browse for output file path"""
        filename = filedialog.asksaveasfilename(
            title="Save Minecraft Version As",
            defaultextension=".appx",
            filetypes=[("APPX files", "*.appx"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            
    def start_download(self):
        """Start download process"""
        if not self.selected_version:
            messagebox.showerror("Error", "Please select a version to download")
            return
            
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output path")
            return
            
        if self.selected_version['version_type'] == 1 and not self.msa_token.get():
            result = messagebox.askyesno(
                "Beta Version Notice",
                "This is a beta version of Minecraft Bedrock.\n\n"
                "While MSA authentication is technically required for beta versions, "
                "many beta versions can still be downloaded without it.\n\n"
                "The MSA token is needed for:\n"
                "• Insider/Preview builds that require Xbox Game Pass\n"
                "• Versions exclusive to beta participants\n"
                "• Private testing versions\n\n"
                "Continue download without MSA token?",
                icon="question"
            )
            if not result:
                return
                
        self.download_cancelled = False
                
        self.download_thread = threading.Thread(target=self.download_version, daemon=True)
        self.download_thread.start()
        
        self.download_btn.config(state=tk.DISABLED, text="Downloading...")
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
    def download_version(self):
        """Download selected version (runs in separate thread)"""
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            version = self.selected_version
            output_path = self.output_path.get()
            
            self.root.after(0, self.log_message, f"🚀 Starting download: {version['name']}")
            self.root.after(0, self.download_status.set, "Initializing download...")
            
            async def download_async():
                async with VersionDownloader() as downloader:
                    if self.msa_token.get():
                        downloader.enable_user_authorization(self.msa_token.get())
                        
                    await downloader.download(
                        version['uuid'],
                        "1", 
                        output_path,
                        self.progress_callback
                    )
                    
            if self.download_cancelled:
                self.root.after(0, self.download_complete, False, "Download cancelled")
                return
                
            try:
                self.download_task = loop.create_task(download_async())
                loop.run_until_complete(self.download_task)
                
            except asyncio.CancelledError:
                self.root.after(0, self.download_complete, False, "Download cancelled by user")
                return
            except Exception as e:
                if "cancelled" in str(e).lower():
                    self.root.after(0, self.download_complete, False, "Download cancelled by user")
                    return
                else:
                    raise
            
            if self.download_cancelled:
                self.root.after(0, self.download_complete, False, "Download cancelled")
                return
            
            self.root.after(0, self.download_complete, True, None)
            
        except BadUpdateIdentityException:
            error_msg = "Unable to fetch download URL"
            if self.selected_version and self.selected_version['version_type'] == 1:  # Beta
                error_msg += "\n\nFor beta versions, ensure:\n1. Your account is subscribed to Minecraft beta\n2. You have provided a valid MSA token"
            self.root.after(0, self.download_complete, False, error_msg)
            
        except Exception as e:
            self.root.after(0, self.download_complete, False, str(e))
            
        finally:
            if loop and not loop.is_closed():
                loop.close()
            self.download_task = None
            
    def progress_callback(self, downloaded: int, total: int):
        """Progress callback for downloads"""
        if self.download_cancelled:
            return
            
        if total and total > 0:
            percentage = (downloaded / total) * 100
            self.root.after(0, self.progress_var.set, percentage)
            status = f"Downloaded: {format_size(downloaded)} / {format_size(total)} ({percentage:.1f}%)"
        else:
            status = f"Downloaded: {format_size(downloaded)}"
            
        self.root.after(0, self.download_status.set, status)
        
        if self.download_cancelled:
            raise asyncio.CancelledError("Download cancelled by user")
        
    def download_complete(self, success: bool, error: str = None):
        """Handle download completion with modern notifications"""
        self.download_btn.config(state=tk.NORMAL, text="Download Selected Version")
        self.cancel_btn.config(state=tk.DISABLED)
        self.download_cancelled = False
        self.download_task = None
        self.download_thread = None
        
        if success:
            self.progress_var.set(100)
            self.download_status.set("Download completed successfully!")
            self.log_message(f"✅ Download completed: {self.output_path.get()}")
            
            self.show_success_notification("Download completed successfully!")
        else:
            self.progress_var.set(0)
            self.download_status.set("Download failed")
            self.log_message(f"❌ Download failed: {error}")
            
            self.show_error_notification(f"Download failed:\n{error}")
            
    def show_success_notification(self, message: str):
        """Show modern success notification"""
        notification = tk.Toplevel(self.root)
        notification.title("Success")
        notification.geometry("350x120")
        notification.configure(bg=COLORS['surface'])
        notification.resizable(False, False)
        
        notification.transient(self.root)
        notification.grab_set()
        
        content = tk.Frame(notification, bg=COLORS['surface'], padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        msg_frame = tk.Frame(content, bg=COLORS['surface'])
        msg_frame.pack(fill=tk.X, pady=(0, 15))
        
        icon_label = ttk.Label(msg_frame, text="✓", font=('Segoe UI', 20, 'bold'),
                              foreground=COLORS['success'], background=COLORS['surface'])
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        msg_label = ttk.Label(msg_frame, text=message, font=('Segoe UI', 9),
                             background=COLORS['surface'], foreground=COLORS['text'])
        msg_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ok_btn = ttk.Button(content, text="OK", command=notification.destroy,
                           style='Modern.TButton')
        ok_btn.pack(anchor=tk.E)
        
        notification.after(3000, notification.destroy)
        
    def show_error_notification(self, message: str):
        """Show modern error notification"""
        notification = tk.Toplevel(self.root)
        notification.title("Error")
        notification.geometry("400x150")
        notification.configure(bg=COLORS['surface'])
        notification.resizable(False, False)
        
        notification.transient(self.root)
        notification.grab_set()
        
        content = tk.Frame(notification, bg=COLORS['surface'], padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        msg_frame = tk.Frame(content, bg=COLORS['surface'])
        msg_frame.pack(fill=tk.X, pady=(0, 15))
        
        icon_label = ttk.Label(msg_frame, text="✗", font=('Segoe UI', 20, 'bold'),
                              foreground=COLORS['error'], background=COLORS['surface'])
        icon_label.pack(side=tk.LEFT, padx=(0, 10), anchor=tk.N)
        
        msg_label = ttk.Label(msg_frame, text=message, font=('Segoe UI', 9),
                             background=COLORS['surface'], foreground=COLORS['text'],
                             wraplength=320)
        msg_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ok_btn = ttk.Button(content, text="OK", command=notification.destroy,
                           style='Modern.TButton')
        ok_btn.pack(anchor=tk.E)
            
    def cancel_download(self):
        """Cancel current download"""
        if self.download_thread and self.download_thread.is_alive():
            self.log_message("🚫 Cancelling download...")
            self.download_status.set("Cancelling...")
            self.download_cancelled = True
            
            if self.download_task and not self.download_task.done():
                self.download_task.cancel()
                self.log_message("🚫 Async task cancelled")
            
            def force_cleanup():
                if self.output_path.get() and os.path.exists(self.output_path.get()):
                    try:
                        os.remove(self.output_path.get())
                        self.log_message("🗑️ Cleaned up partial download file")
                    except Exception as e:
                        self.log_message(f"⚠️ Could not clean up partial file: {e}")
                
                self.download_btn.config(state=tk.NORMAL, text="Download Selected Version")
                self.cancel_btn.config(state=tk.DISABLED)
                self.progress_var.set(0)
                self.download_status.set("Download cancelled")
                
                self.download_thread = None
                self.download_task = None
                self.download_cancelled = False
                
            self.root.after(2000, force_cleanup)
        else:
            self.download_btn.config(state=tk.NORMAL, text="Download Selected Version")
            self.cancel_btn.config(state=tk.DISABLED)
            self.progress_var.set(0)
            self.download_status.set("Ready")
            self.download_cancelled = False
        
    def open_download_folder(self):
        """Open the download folder"""
        if self.output_path.get():
            folder = os.path.dirname(self.output_path.get())
            if folder and os.path.exists(folder):
                os.startfile(folder)
            else:
                os.startfile(".")
        else:
            os.startfile(".")
            
    def show_token_help(self):
        """Show help for getting MSA token with modern dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("MSA Token Information")
        help_window.geometry("520x450")
        help_window.configure(bg=COLORS['surface'])
        help_window.resizable(False, False)
        
        help_window.transient(self.root)
        help_window.grab_set()
        
        content = tk.Frame(help_window, bg=COLORS['surface'], padx=30, pady=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(content, text="MSA Token Information", 
                               style='Heading.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        help_text = """MSA (Microsoft Account) Token - What You Need to Know:

What is it?
The MSA token is Microsoft's authentication token for Xbox Live services.

When is it needed?
- Exclusive insider preview builds
- Private beta versions for Xbox Game Pass subscribers  
- Versions restricted to specific Microsoft programs

Good news:
Most beta versions in the public list can be downloaded WITHOUT an MSA token!
The Windows Update system often allows downloads even without authentication.

How to get an MSA token (if needed):
1. Sign up for Xbox Game Pass Ultimate
2. Join the Minecraft Beta program through Xbox Insider Hub
3. Use specialized tools to extract the token from Xbox authentication

Important:
- Only needed for truly restricted versions
- Try downloading first - it usually works without token
- Most "beta" versions are actually public builds
"""
        
        text_widget = tk.Text(content, wrap=tk.WORD, height=12, width=50,
                             font=('Segoe UI', 9), bg=COLORS['surface'],
                             fg=COLORS['text'], relief='flat', borderwidth=0)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        text_widget.insert(1.0, help_text)
        text_widget.configure(state='disabled')
        
        close_btn = ttk.Button(content, text="Close", command=help_window.destroy,
                              style='Modern.TButton')
        close_btn.pack(anchor=tk.E)
        
    def show_about(self):
        """Show about dialog with modern styling"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("450x350")
        about_window.configure(bg=COLORS['surface'])
        about_window.resizable(False, False)
        
        about_window.transient(self.root)
        about_window.grab_set()
        
        content = tk.Frame(about_window, bg=COLORS['surface'], padx=30, pady=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(content, text="Minecraft Bedrock", 
                               style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        subtitle_label = ttk.Label(content, text="Version Downloader", 
                                  style='Heading.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(0, 20))
        
        about_text = """A Python GUI application for downloading Minecraft Bedrock versions using WU Protocol.

Version: 1.0
Author: Seraphic Studio
"""
        
        text_widget = tk.Text(content, wrap=tk.WORD, height=8, width=45,
                             font=('Segoe UI', 9), bg=COLORS['surface'],
                             fg=COLORS['text'], relief='flat', borderwidth=0)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        text_widget.insert(1.0, about_text)
        text_widget.configure(state='disabled')
        
        close_btn = ttk.Button(content, text="Close", command=about_window.destroy,
                              style='Modern.TButton')
        close_btn.pack(anchor=tk.E)
        
    def show_error(self, message: str):
        """Show modern error message"""
        self.show_error_notification(message)
        self.download_status.set("Error occurred")
        
    def toggle_dark_mode(self):
        """Toggle between light and dark mode"""
        global COLORS
        
        self.dark_mode.set(not self.dark_mode.get())
        
        if self.dark_mode.get():
            COLORS = DARK_COLORS
        else:
            COLORS = LIGHT_COLORS
        
        self.configure_modern_style()
        
        self.update_theme_recursive(self.root)
        
        if hasattr(self, 'dark_mode_btn'):
            self.dark_mode_btn.configure(text="☀️ Light" if self.dark_mode.get() else "🌙 Dark")
    
    def update_theme_recursive(self, widget):
        """Recursively update theme for all widgets"""
        widget.configure(bg=COLORS['bg'])
        
        for child in widget.winfo_children():
            try:
                if isinstance(child, tk.Frame):
                    if 'Card' in str(child.cget('relief')) or child.cget('bg') in ['#ffffff', '#2d2d2d']:
                        child.configure(bg=COLORS['surface'])
                        # Update frame highlighting
                        child.configure(highlightbackground=COLORS['surface'], highlightthickness=0)
                    else:
                        child.configure(bg=COLORS['bg'])
                elif isinstance(child, tk.Label):
                    child.configure(bg=COLORS['surface'], fg=COLORS['text'])
                elif isinstance(child, scrolledtext.ScrolledText):
                    # Update ScrolledText with no highlighting
                    child.configure(bg=COLORS['surface'], fg=COLORS['text'],
                                  selectbackground=COLORS['surface'], selectforeground=COLORS['text'],
                                  highlightbackground=COLORS['surface'], highlightthickness=0)
                elif isinstance(child, tk.Entry):
                    # Update Entry widgets with no highlighting
                    child.configure(bg=COLORS['surface'], fg=COLORS['text'],
                                  selectbackground=COLORS['surface'], selectforeground=COLORS['text'],
                                  highlightbackground=COLORS['surface'], highlightthickness=0)
                elif isinstance(child, tk.Text):
                    # Update Text widgets with no highlighting
                    child.configure(bg=COLORS['surface'], fg=COLORS['text'],
                                  selectbackground=COLORS['surface'], selectforeground=COLORS['text'],
                                  highlightbackground=COLORS['surface'], highlightthickness=0)
                
                self.update_theme_recursive(child)
            except tk.TclError:
                pass


def main():
    """Main function to run the GUI"""
    try:
        if sys.platform == 'win32':
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
                
        root = tk.Tk()
        
        try:
            #root.iconbitmap('icon.ico')
            pass
        except:
            pass
            
        app = DownloaderGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Startup Error", f"Error starting GUI: {e}")


if __name__ == "__main__":
    main()
