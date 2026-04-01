#!/usr/bin/env python3
"""
Cybersecurity Process Monitor Dashboard - Modern Minimal Design
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import subprocess
import threading
import psutil
import pandas as pd
from datetime import datetime
import platform
import json
import signal
from PIL import Image, ImageTk  # Optional: for better icons

class ModernProcessDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Monitor")
        self.root.geometry("1400x850")
        
        # Modern color palette
        self.colors = {
            'bg': '#0a0a0f',           # Dark background
            'bg_secondary': '#111114',   # Slightly lighter
            'fg': '#e4e4e7',            # Light text
            'fg_secondary': '#71717a',   # Dim text
            'accent': '#3b82f6',         # Electric blue
            'accent_hover': '#2563eb',   # Darker blue
            'success': '#10b981',        # Emerald green
            'warning': '#f59e0b',        # Amber
            'danger': '#ef4444',         # Red
            'purple': '#8b5cf6',         # Purple
            'border': '#27272a'          # Border color
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Setup custom styles
        self.setup_styles()
        
        # Variables
        self.update_thread_running = False
        
        # Create main layout
        self.create_widgets()
        
        # Bind keyboard shortcuts
        self.setup_shortcuts()
        
        # Initial data load
        self.refresh_processes()
        
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure treeview
        style.configure("Modern.Treeview",
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['fg'],
                       fieldbackground=self.colors['bg_secondary'],
                       borderwidth=0,
                       highlightthickness=0,
                       rowheight=28,
                       font=('Segoe UI', 9))
        
        style.map('Modern.Treeview',
                  background=[('selected', self.colors['accent'])],
                  foreground=[('selected', 'white')])
        
        # Treeview heading
        style.configure("Modern.Treeview.Heading",
                       background=self.colors['bg'],
                       foreground=self.colors['fg_secondary'],
                       borderwidth=0,
                       relief='flat',
                       font=('Segoe UI', 9, 'bold'))
        
        style.map('Modern.Treeview.Heading',
                  background=[('active', self.colors['bg_secondary'])])
        
        # Buttons
        style.configure("Modern.TButton",
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       focusthickness=0,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        
        style.map('Modern.TButton',
                  background=[('active', self.colors['bg'])],
                  foreground=[('active', self.colors['accent'])])
        
        # Accent button
        style.configure("Accent.TButton",
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0)
        
        style.map('Accent.TButton',
                  background=[('active', self.colors['accent_hover'])])
        
        # LabelFrame
        style.configure("Modern.TLabelframe",
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure("Modern.TLabelframe.Label",
                       background=self.colors['bg'],
                       foreground=self.colors['fg_secondary'],
                       font=('Segoe UI', 9, 'bold'))
        
        # Entry
        style.configure("Modern.TEntry",
                       fieldbackground=self.colors['bg_secondary'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       lightcolor=self.colors['border'],
                       darkcolor=self.colors['border'],
                       focuscolor=self.colors['accent'])
        
        # Checkbutton
        style.configure("Modern.TCheckbutton",
                       background=self.colors['bg'],
                       foreground=self.colors['fg_secondary'],
                       focusthickness=0)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<F5>', lambda e: self.refresh_processes())
        self.root.bind('<Control-f>', lambda e: self.filter_entry.focus())
        self.root.bind('<Escape>', lambda e: self.clear_filter())
        
    def create_widgets(self):
        """Create all dashboard widgets with modern design"""
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(main_container)
        
        # Control bar
        self.create_control_bar(main_container)
        
        # Main content area (split view)
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Process table
        self.create_process_table(content_frame)
        
        # Bottom panels
        bottom_frame = tk.Frame(main_container, bg=self.colors['bg'])
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Console and stats in a grid
        self.create_bottom_panels(bottom_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self, parent):
        """Create modern header with gradient effect"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Left side - Title and badge
        left_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        left_frame.pack(side=tk.LEFT)
        
        # Title with icon
        title_font = font.Font(family='Segoe UI', size=20, weight='bold')
        title_label = tk.Label(left_frame, text="🔍 Process Monitor", 
                               font=title_font, bg=self.colors['bg'], fg=self.colors['fg'])
        title_label.pack(side=tk.LEFT)
        
        # Version badge
        badge = tk.Label(left_frame, text=" v1.0", 
                        font=('Segoe UI', 10), bg=self.colors['bg'], fg=self.colors['fg_secondary'])
        badge.pack(side=tk.LEFT, padx=(8, 0), pady=(5, 0))
        
        # Right side - System info
        right_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        right_frame.pack(side=tk.RIGHT)
        
        # System info with icons
        sys_info = f"{platform.system()} {platform.release()}"
        sys_label = tk.Label(right_frame, text=f"💻 {sys_info}", 
                            font=('Segoe UI', 10), bg=self.colors['bg'], fg=self.colors['fg_secondary'])
        sys_label.pack(side=tk.RIGHT)
        
        # Separator
        sep = tk.Frame(parent, height=1, bg=self.colors['border'])
        sep.pack(fill=tk.X, pady=(0, 10))
        
    def create_control_bar(self, parent):
        """Create modern control bar with buttons and filters"""
        control_frame = tk.Frame(parent, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button container
        button_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        button_frame.pack(side=tk.LEFT)
        
        # Buttons with modern styling
        buttons = [
            ("🔄 Refresh", self.refresh_processes, False),
            ("⏺ Auto-refresh", self.toggle_auto_refresh, True),
            ("📊 Export", self.export_to_csv, False),
            ("⚠️ Kill", self.kill_selected_process, False)
        ]
        
        self.auto_refresh_var = tk.BooleanVar()
        
        for text, command, is_check in buttons:
            if is_check:
                btn = ttk.Checkbutton(button_frame, text=text, 
                                     variable=self.auto_refresh_var,
                                     command=command,
                                     style='Modern.TCheckbutton')
            else:
                btn = ttk.Button(button_frame, text=text, 
                                command=command, style='Modern.TButton')
            btn.pack(side=tk.LEFT, padx=4)
        
        # Separator
        sep = tk.Frame(control_frame, width=1, bg=self.colors['border'])
        sep.pack(side=tk.LEFT, padx=15, fill=tk.Y)
        
        # Filter section
        filter_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        filter_label = tk.Label(filter_frame, text="🔍", 
                               bg=self.colors['bg'], fg=self.colors['fg_secondary'])
        filter_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', lambda *args: self.filter_processes())
        
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, 
                                     style='Modern.TEntry', width=30)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Clear filter button
        clear_btn = tk.Label(filter_frame, text="✕", 
                            bg=self.colors['bg'], fg=self.colors['fg_secondary'],
                            cursor='hand2', font=('Segoe UI', 10, 'bold'))
        clear_btn.pack(side=tk.LEFT, padx=(8, 0))
        clear_btn.bind('<Button-1>', lambda e: self.clear_filter())
        
        # Stats badge
        self.stats_badge = tk.Label(control_frame, text="0 processes", 
                                   bg=self.colors['bg_secondary'], fg=self.colors['accent'],
                                   font=('Segoe UI', 9), padx=12, pady=4)
        self.stats_badge.pack(side=tk.RIGHT)
        
    def create_process_table(self, parent):
        """Create modern process table"""
        # Table container with border
        table_container = tk.Frame(parent, bg=self.colors['border'], bd=1, relief='solid')
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Inner frame
        table_frame = tk.Frame(table_container, bg=self.colors['bg_secondary'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical')
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal')
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ('PID', 'Name', 'CPU%', 'Memory%', 'Status', 'User', 'Command')
        
        self.process_tree = ttk.Treeview(table_frame, columns=columns, 
                                         show='headings',
                                         yscrollcommand=v_scrollbar.set,
                                         xscrollcommand=h_scrollbar.set,
                                         style='Modern.Treeview')
        self.process_tree.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.process_tree.yview)
        h_scrollbar.config(command=self.process_tree.xview)
        
        # Configure columns
        column_configs = {
            'PID': {'width': 70, 'anchor': 'center'},
            'Name': {'width': 200, 'anchor': 'w'},
            'CPU%': {'width': 80, 'anchor': 'e'},
            'Memory%': {'width': 90, 'anchor': 'e'},
            'Status': {'width': 100, 'anchor': 'center'},
            'User': {'width': 180, 'anchor': 'w'},
            'Command': {'width': 400, 'anchor': 'w'}
        }
        
        for col, config in column_configs.items():
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=config['width'], anchor=config['anchor'])
        
        # Configure tags for different states
        self.process_tree.tag_configure('high_cpu', foreground='#f97316')
        self.process_tree.tag_configure('high_memory', foreground='#ef4444')
        self.process_tree.tag_configure('system', foreground='#10b981')
        self.process_tree.tag_configure('stopped', foreground='#6b7280')
        
    def create_bottom_panels(self, parent):
        """Create bottom panels with modern design"""
        # Left panel - Console
        console_frame = tk.LabelFrame(parent, text="  PowerShell Console  ", 
                                     bg=self.colors['bg'], fg=self.colors['fg_secondary'],
                                     font=('Segoe UI', 10, 'bold'))
        console_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        self.console_output = scrolledtext.ScrolledText(console_frame, 
                                                        bg=self.colors['bg_secondary'],
                                                        fg=self.colors['fg'],
                                                        font=('Consolas', 9),
                                                        insertbackground=self.colors['accent'],
                                                        relief='flat',
                                                        borderwidth=0)
        self.console_output.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Console header buttons
        console_buttons = tk.Frame(console_frame, bg=self.colors['bg'])
        console_buttons.pack(fill=tk.X, pady=(5, 0))
        
        clear_console_btn = tk.Button(console_buttons, text="Clear", 
                                     command=self.clear_console,
                                     bg=self.colors['bg_secondary'],
                                     fg=self.colors['fg_secondary'],
                                     relief='flat',
                                     cursor='hand2')
        clear_console_btn.pack(side=tk.LEFT, padx=2)
        
        # Right panel - Statistics
        stats_frame = tk.LabelFrame(parent, text="  System Statistics  ",
                                   bg=self.colors['bg'], fg=self.colors['fg_secondary'],
                                   font=('Segoe UI', 10, 'bold'))
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame,
                                                   bg=self.colors['bg_secondary'],
                                                   fg=self.colors['fg'],
                                                   font=('Consolas', 9),
                                                   relief='flat',
                                                   borderwidth=0)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
    def create_status_bar(self):
        """Create modern status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    bg=self.colors['bg_secondary'], 
                                    fg=self.colors['fg_secondary'],
                                    font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)
        
        # Live time
        self.time_label = tk.Label(status_frame, text="", 
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['fg_secondary'],
                                  font=('Segoe UI', 9))
        self.time_label.pack(side=tk.RIGHT, padx=15, pady=5)
        self.update_time()
        
    def update_time(self):
        """Update time in status bar"""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_label.config(text=f"🕒 {current_time}")
        self.root.after(1000, self.update_time)
        
    def refresh_processes(self):
        """Refresh process data with modern display"""
        self.status_label.config(text="Refreshing processes...")
        
        # Clear tree
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        process_count = 0
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                            'status', 'username', 'cmdline']):
                try:
                    pinfo = proc.info
                    if pinfo['name']:
                        cpu = pinfo['cpu_percent'] or 0
                        memory = pinfo['memory_percent'] or 0
                        status = pinfo['status'] or 'unknown'
                        user = pinfo['username'] or 'N/A'
                        cmd = ' '.join(pinfo['cmdline'])[:80] if pinfo['cmdline'] else 'N/A'
                        
                        values = (
                            pinfo['pid'],
                            pinfo['name'][:60],
                            f"{cpu:.1f}",
                            f"{memory:.1f}",
                            status.capitalize(),
                            user,
                            cmd
                        )
                        
                        # Determine tags
                        tags = []
                        if cpu > 50:
                            tags.append('high_cpu')
                        if memory > 50:
                            tags.append('high_memory')
                        if user == 'NT AUTHORITY\\SYSTEM':
                            tags.append('system')
                        if status == 'stopped':
                            tags.append('stopped')
                        
                        self.process_tree.insert('', tk.END, values=values, tags=tags)
                        process_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            self.status_label.config(text=f"✓ Loaded {process_count} processes")
            self.stats_badge.config(text=f"{process_count} processes")
            self.log_to_console(f"Refreshed {process_count} processes")
            self.update_statistics()
            
        except Exception as e:
            self.status_label.config(text=f"✗ Error: {str(e)}")
            self.log_to_console(f"Refresh error: {str(e)}", error=True)
            
    def update_statistics(self):
        """Update statistics panel with modern metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get top processes
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except:
                    continue
                    
            # Sort processes
            top_cpu = sorted([p for p in processes if p['cpu_percent']], 
                           key=lambda x: x['cpu_percent'], reverse=True)[:5]
            top_memory = sorted([p for p in processes if p['memory_percent']], 
                              key=lambda x: x['memory_percent'], reverse=True)[:5]
            
            # Build statistics display
            self.stats_text.delete(1.0, tk.END)
            
            # System metrics with visual bars
            self.stats_text.insert(tk.END, "💻 SYSTEM\n", 'header')
            self.stats_text.insert(tk.END, "─" * 35 + "\n", 'separator')
            
            # CPU with bar
            cpu_bar = self.create_bar(cpu_percent)
            self.stats_text.insert(tk.END, f"CPU    {cpu_percent:>5.1f}% {cpu_bar}\n")
            
            # Memory with bar
            mem_bar = self.create_bar(memory.percent)
            self.stats_text.insert(tk.END, f"Memory {memory.percent:>5.1f}% {mem_bar}\n")
            self.stats_text.insert(tk.END, f"       {memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB\n\n")
            
            # Top processes
            self.stats_text.insert(tk.END, "🔥 TOP CPU\n", 'header')
            self.stats_text.insert(tk.END, "─" * 35 + "\n", 'separator')
            for proc in top_cpu:
                name = proc['name'][:25] if proc['name'] else 'Unknown'
                cpu = proc['cpu_percent']
                bar = self.create_bar(cpu)
                self.stats_text.insert(tk.END, f"{name:<25} {cpu:>5.1f}% {bar}\n")
            
            self.stats_text.insert(tk.END, "\n💾 TOP MEMORY\n", 'header')
            self.stats_text.insert(tk.END, "─" * 35 + "\n", 'separator')
            for proc in top_memory:
                name = proc['name'][:25] if proc['name'] else 'Unknown'
                mem = proc['memory_percent']
                bar = self.create_bar(mem)
                self.stats_text.insert(tk.END, f"{name:<25} {mem:>5.1f}% {bar}\n")
            
            # Configure text tags
            self.stats_text.tag_config('header', foreground=self.colors['accent'], font=('Segoe UI', 9, 'bold'))
            self.stats_text.tag_config('separator', foreground=self.colors['fg_secondary'])
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"Error: {str(e)}")
            
    def create_bar(self, percentage, width=20):
        """Create a visual bar for percentages"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return bar
        
    def filter_processes(self):
        """Filter processes by name"""
        filter_text = self.filter_var.get().lower()
        
        # Clear tree
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        filtered_count = 0
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                            'status', 'username', 'cmdline']):
                try:
                    pinfo = proc.info
                    if pinfo['name'] and filter_text in pinfo['name'].lower():
                        cpu = pinfo['cpu_percent'] or 0
                        memory = pinfo['memory_percent'] or 0
                        status = pinfo['status'] or 'unknown'
                        user = pinfo['username'] or 'N/A'
                        cmd = ' '.join(pinfo['cmdline'])[:80] if pinfo['cmdline'] else 'N/A'
                        
                        values = (
                            pinfo['pid'],
                            pinfo['name'][:60],
                            f"{cpu:.1f}",
                            f"{memory:.1f}",
                            status.capitalize(),
                            user,
                            cmd
                        )
                        
                        tags = []
                        if cpu > 50:
                            tags.append('high_cpu')
                        if memory > 50:
                            tags.append('high_memory')
                        if status == 'stopped':
                            tags.append('stopped')
                            
                        self.process_tree.insert('', tk.END, values=values, tags=tags)
                        filtered_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            self.status_label.config(text=f"Filtered: {filtered_count} processes")
            self.stats_badge.config(text=f"{filtered_count} / {filtered_count} filtered")
            
        except Exception as e:
            self.log_to_console(f"Filter error: {str(e)}", error=True)
            
    def clear_filter(self):
        """Clear the filter"""
        self.filter_var.set("")
        self.filter_entry.focus()
        self.refresh_processes()
        
    def kill_selected_process(self):
        """Kill selected process with confirmation"""
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a process to kill")
            return
            
        item = self.process_tree.item(selected[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        # Custom confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Process Termination",
            f"⚠️ Are you sure you want to terminate:\n\n{name} (PID: {pid})\n\nThis action cannot be undone!",
            icon='warning'
        )
        
        if confirm:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                self.log_to_console(f"✓ Process {name} (PID: {pid}) terminated")
                self.refresh_processes()
            except psutil.NoSuchProcess:
                messagebox.showerror("Error", "Process no longer exists")
            except psutil.AccessDenied:
                messagebox.showerror("Error", "Access denied. Run as Administrator")
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
                
    def export_to_csv(self):
        """Export process data to CSV"""
        try:
            data = []
            for item in self.process_tree.get_children():
                values = self.process_tree.item(item)['values']
                data.append({
                    'PID': values[0],
                    'Name': values[1],
                    'CPU%': values[2],
                    'Memory%': values[3],
                    'Status': values[4],
                    'User': values[5],
                    'Command': values[6],
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            if not data:
                messagebox.showwarning("No Data", "No processes to export")
                return
                
            filename = f"process_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            self.log_to_console(f"✓ Exported {len(data)} processes to {filename}")
            messagebox.showinfo("Export Complete", f"Saved to:\n{os.path.abspath(filename)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            
    def toggle_auto_refresh(self):
        """Toggle auto-refresh functionality"""
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
            
    def start_auto_refresh(self):
        """Start auto-refresh"""
        self.update_thread_running = True
        self.log_to_console("Auto-refresh enabled (5s interval)")
        self.auto_refresh()
        
    def stop_auto_refresh(self):
        """Stop auto-refresh"""
        self.update_thread_running = False
        self.log_to_console("Auto-refresh disabled")
        
    def auto_refresh(self):
        """Auto-refresh process data"""
        if self.update_thread_running:
            self.refresh_processes()
            self.root.after(5000, self.auto_refresh)
            
    def log_to_console(self, message, error=False):
        """Log message to console"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        prefix = "✗" if error else "✓"
        color = self.colors['danger'] if error else self.colors['success']
        
        self.console_output.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.console_output.see(tk.END)
        
    def clear_console(self):
        """Clear console output"""
        self.console_output.delete(1.0, tk.END)
        self.log_to_console("Console cleared")

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = ModernProcessDashboard(root)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Handle window close
        def on_closing():
            if app.update_thread_running:
                app.update_thread_running = False
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()