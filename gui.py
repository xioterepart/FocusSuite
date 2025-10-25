import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import DateEntry  # For date picker
from database import (init_db, add_task, get_tasks, delete_task, mark_task_done,
                     add_habit, get_habits, check_habit, delete_habit, update_task_priority,
                     update_habit_name, reset_habit_streak)
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
from ai_engine import ai_engine
from gamification import gamification
from theme import theme, theme_manager, ModernTheme
from focus_mode import focus_timer
import threading
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎯 FocusSuite - AI-Powered Productivity")
        self.geometry("1200x800")
        
        # Set app icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'app.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass
        
        # Configure background
        self.configure(bg=ModernTheme.get_bg())
        
        # Apply modern theme
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        theme_manager.configure_style(self.style)
        
        # Initialize gamification
        gamification.update_daily_stats()
        
        # Create header and main content
        self.create_header()
        
        # Notebook tabs
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill='both', expand=True, padx=10, pady=10)

        self.dashboard_frame = ttk.Frame(self.nb)
        self.tasks_frame = ttk.Frame(self.nb)
        self.habits_frame = ttk.Frame(self.nb)
        self.focus_frame = ttk.Frame(self.nb)
        self.ai_frame = ttk.Frame(self.nb)
        self.achievements_frame = ttk.Frame(self.nb)

        self.nb.add(self.dashboard_frame, text="📊 Dashboard")
        self.nb.add(self.tasks_frame, text="✅ Tasks")
        self.nb.add(self.habits_frame, text="🎯 Habits")
        self.nb.add(self.focus_frame, text="🧘 Focus Mode")
        self.nb.add(self.ai_frame, text="🤖 AI Insights")
        self.nb.add(self.achievements_frame, text="🏆 Achievements")

        self.build_dashboard_tab()
        self.build_tasks_tab()
        self.build_habits_tab()
        self.build_focus_tab()
        self.build_ai_tab()
        self.build_achievements_tab()
        
        # Update AI priorities on startup
        self.update_ai_priorities_silent()
        self.check_achievements()
    
    def create_header(self):
        """Create modern header with logo, gamification stats, and dark mode toggle"""
        self.header = tk.Frame(self, bg=ModernTheme.get_bg_secondary(), height=90)
        self.header.pack(fill='x', padx=0, pady=0)
        self.header.pack_propagate(False)
        
        # Left side - Logo and App title
        left_frame = tk.Frame(self.header, bg=ModernTheme.get_bg_secondary())
        left_frame.pack(side='left', padx=20, pady=10)
        
        # Try to load logo
        try:
            from PIL import Image, ImageTk
            logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(left_frame, image=self.logo_photo, bg=ModernTheme.get_bg_secondary())
                logo_label.pack(side='left', padx=(0, 15))
        except:
            pass
        
        title_frame = tk.Frame(left_frame, bg=ModernTheme.get_bg_secondary())
        title_frame.pack(side='left')
        
        title = tk.Label(title_frame, text="FocusSuite",
                        font=('Segoe UI', 22, 'bold'),
                        bg=ModernTheme.get_bg_secondary(),
                        fg=ModernTheme.PRIMARY_BLUE)
        title.pack(anchor='w')
        
        subtitle = tk.Label(title_frame, text="AI-Powered Productivity Platform",
                           font=('Segoe UI', 9),
                           bg=ModernTheme.get_bg_secondary(),
                           fg=ModernTheme.get_text_secondary())
        subtitle.pack(anchor='w')
        
        # Right side - Gamification stats
        self.stats_frame = tk.Frame(self.header, bg=ModernTheme.get_bg_secondary())
        self.stats_frame.pack(side='right', padx=20, pady=10)
        
        self.update_header_stats()
    
    def update_header_stats(self):
        """Update header statistics"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stats = gamification.get_stats()
        
        # Level badge
        self.create_stat_badge(self.stats_frame, "⭐", f"Level {stats['level']}", 
                              ModernTheme.LEVEL_COLOR).pack(side='left', padx=5)
        
        # XP badge
        xp_progress = stats['xp_progress']
        xp_text = f"{int(xp_progress['current_xp'])}/{xp_progress['xp_needed']} XP"
        self.create_stat_badge(self.stats_frame, "✨", xp_text, 
                              ModernTheme.XP_COLOR).pack(side='left', padx=5)
        
        # Streak badge
        streak_text = f"{stats['consecutive_days']} days"
        self.create_stat_badge(self.stats_frame, "🔥", streak_text, 
                              ModernTheme.STREAK_COLOR).pack(side='left', padx=5)
        
        # Achievements badge
        ach_text = f"{stats['achievements_unlocked']}/{stats['total_achievements']}"
        self.create_stat_badge(self.stats_frame, "🏆", ach_text, 
                              ModernTheme.ACHIEVEMENT_COLOR).pack(side='left', padx=5)
    
    def create_stat_badge(self, parent, icon, text, color):
        """Create a stat badge"""
        frame = tk.Frame(parent, bg=ModernTheme.get_card_bg(), 
                        highlightbackground=color, highlightthickness=2)
        
        label = tk.Label(frame, text=f"{icon} {text}",
                        font=('Segoe UI', 10, 'bold'),
                        bg=ModernTheme.get_card_bg(), fg=color,
                        padx=12, pady=6)
        label.pack()
        
        return frame
    
    # Dark mode functionality removed per user request

    # ---------------- Dashboard Tab ----------------
    def build_dashboard_tab(self):
        """Dashboard with overview and analytics"""
        self.dashboard_container = tk.Frame(self.dashboard_frame, bg=ModernTheme.get_bg())
        self.dashboard_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Clear existing widgets
        for widget in self.dashboard_container.winfo_children():
            widget.destroy()
        
        # Quick stats
        stats_frame = tk.Frame(self.dashboard_container, bg=ModernTheme.get_bg())
        stats_frame.pack(fill='x', pady=(0, 20))
        
        tasks = get_tasks()
        habits = get_habits()
        completed = [t for t in tasks if t[6] == 'Done']
        pending = [t for t in tasks if t[6] != 'Done']
        
        self.create_stat_card(stats_frame, "Total Tasks", len(tasks), ModernTheme.INFO).pack(side='left', padx=10, expand=True, fill='both')
        self.create_stat_card(stats_frame, "Completed", len(completed), ModernTheme.SUCCESS).pack(side='left', padx=10, expand=True, fill='both')
        self.create_stat_card(stats_frame, "Pending", len(pending), ModernTheme.WARNING).pack(side='left', padx=10, expand=True, fill='both')
        self.create_stat_card(stats_frame, "Habits", len(habits), ModernTheme.SECONDARY_BLUE).pack(side='left', padx=10, expand=True, fill='both')
        
        # Charts
        charts_frame = tk.Frame(self.dashboard_container, bg=ModernTheme.get_bg())
        charts_frame.pack(fill='both', expand=True)
        
        left_chart = theme_manager.create_card_frame(charts_frame)
        left_chart.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(left_chart, text="Task Status", font=('Segoe UI', 14, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text()).pack(pady=10)
        self.create_task_chart(left_chart, tasks)
        
        right_chart = theme_manager.create_card_frame(charts_frame)
        right_chart.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(right_chart, text="Habit Streaks", font=('Segoe UI', 14, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text()).pack(pady=10)
        self.create_habit_chart(right_chart, habits)
    
    def create_stat_card(self, parent, title, value, color):
        """Create a stat card"""
        card = theme_manager.create_card_frame(parent)
        card.configure(width=200, height=120)
        tk.Label(card, text=title, font=('Segoe UI', 11),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text_secondary()).pack(pady=(20, 5))
        tk.Label(card, text=str(value), font=('Segoe UI', 32, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=color).pack()
        return card
    
    def create_task_chart(self, parent, tasks):
        """Create task status pie chart"""
        fig = Figure(figsize=(4, 3), facecolor=ModernTheme.get_card_bg())
        ax = fig.add_subplot(111)
        completed = len([t for t in tasks if t[6] == 'Done'])
        pending = len([t for t in tasks if t[6] != 'Done'])
        if completed == 0 and pending == 0:
            ax.text(0.5, 0.5, 'No tasks yet', ha='center', va='center',
                   fontsize=12, color=ModernTheme.get_text_secondary())
            ax.axis('off')
        else:
            colors = [ModernTheme.SUCCESS, ModernTheme.WARNING]
            ax.pie([completed, pending], labels=['Done', 'Pending'],
                  autopct='%1.1f%%', colors=colors, startangle=90,
                  textprops={'color': ModernTheme.get_text()})
        ax.set_facecolor(ModernTheme.get_card_bg())
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_habit_chart(self, parent, habits):
        """Create habit streaks bar chart"""
        fig = Figure(figsize=(4, 3), facecolor=ModernTheme.get_card_bg())
        ax = fig.add_subplot(111)
        if not habits:
            ax.text(0.5, 0.5, 'No habits yet', ha='center', va='center',
                   fontsize=12, color=ModernTheme.get_text_secondary())
            ax.axis('off')
        else:
            names = [h[1][:15] for h in habits[:5]]
            streaks = [h[2] for h in habits[:5]]
            ax.barh(names, streaks, color=ModernTheme.STREAK_COLOR)
            ax.set_xlabel('Days', color=ModernTheme.get_text_secondary())
            ax.tick_params(colors=ModernTheme.get_text_secondary(), labelsize=9)
            for spine in ax.spines.values():
                spine.set_color(ModernTheme.get_border())
        ax.set_facecolor(ModernTheme.get_card_bg())
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    # ---------------- Tasks Tab ----------------
    def build_tasks_tab(self):
        left = theme_manager.create_card_frame(self.tasks_frame, width=380)
        left.pack(side='left', fill='y', padx=10, pady=10)
        left.pack_propagate(False)  # Maintain fixed width
        right = tk.Frame(self.tasks_frame, bg=ModernTheme.get_bg())
        right.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        tk.Label(left, text="Add New Task", font=('Segoe UI', 14, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text()).pack(pady=10, padx=20)
        
        # Task Title
        tk.Label(left, text="Task Title", bg=ModernTheme.get_card_bg(),
                fg=ModernTheme.get_text_secondary(), font=('Segoe UI', 9, 'bold')).pack(pady=(8, 2), padx=20, anchor='w')
        self.title_entry = tk.Entry(left, width=32, bg=ModernTheme.get_input_bg(),
                                    fg=ModernTheme.get_text(), font=('Segoe UI', 9),
                                    insertbackground=ModernTheme.get_text(), relief='solid', bd=2)
        self.title_entry.pack(pady=3, padx=20, ipady=5, fill='x')
        
        # Deadline - Date Picker
        tk.Label(left, text="Deadline", bg=ModernTheme.get_card_bg(),
                fg=ModernTheme.get_text_secondary(), font=('Segoe UI', 9, 'bold')).pack(pady=(8, 2), padx=20, anchor='w')
        self.deadline_picker = DateEntry(left, width=32, background=ModernTheme.PRIMARY_BLUE,
                                        foreground='white', borderwidth=2, font=('Segoe UI', 9),
                                        date_pattern='yyyy-mm-dd')
        self.deadline_picker.pack(pady=3, padx=20, ipady=5, fill='x')
        
        # Reminder Time - Spinboxes for hours and minutes
        tk.Label(left, text="Reminder Time", bg=ModernTheme.get_card_bg(),
                fg=ModernTheme.get_text_secondary(), font=('Segoe UI', 9, 'bold')).pack(pady=(8, 2), padx=20, anchor='w')
        
        time_frame = tk.Frame(left, bg=ModernTheme.get_card_bg())
        time_frame.pack(pady=3, padx=20, fill='x')
        
        self.hour_spin = tk.Spinbox(time_frame, from_=0, to=23, width=8, font=('Segoe UI', 9),
                                    bg=ModernTheme.get_input_bg(), fg=ModernTheme.get_text(),
                                    insertbackground=ModernTheme.get_text(),
                                    format="%02.0f", relief='solid', bd=2, justify='center')
        self.hour_spin.pack(side='left', padx=(0, 5), ipady=4)
        self.hour_spin.delete(0, 'end')
        self.hour_spin.insert(0, "09")
        
        tk.Label(time_frame, text=":", bg=ModernTheme.get_card_bg(),
                fg=ModernTheme.get_text(), font=('Segoe UI', 12, 'bold')).pack(side='left', padx=5)
        
        self.minute_spin = tk.Spinbox(time_frame, from_=0, to=59, width=8, font=('Segoe UI', 9),
                                      bg=ModernTheme.get_input_bg(), fg=ModernTheme.get_text(),
                                      insertbackground=ModernTheme.get_text(),
                                      format="%02.0f", relief='solid', bd=2, justify='center')
        self.minute_spin.pack(side='left', padx=(5, 0), ipady=4)
        self.minute_spin.delete(0, 'end')
        self.minute_spin.insert(0, "00")
        
        # Repeat - Better styled dropdown
        tk.Label(left, text="Repeat", bg=ModernTheme.get_card_bg(),
                fg=ModernTheme.get_text_secondary(), font=('Segoe UI', 9, 'bold')).pack(pady=(8, 2), padx=20, anchor='w')
        self.repeat_var = tk.StringVar(value="none")
        repeat_combo = ttk.Combobox(left, textvariable=self.repeat_var,
                                    values=["none", "daily", "weekly"], state="readonly", 
                                    width=30, font=('Segoe UI', 9))
        repeat_combo.pack(pady=3, padx=20, ipady=5, fill='x')
        
        btn_frame = tk.Frame(left, bg=ModernTheme.get_card_bg())
        btn_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Button(btn_frame, text="➕ Add Task", command=self.add_task_ui,
                 bg=ModernTheme.PRIMARY_BLUE, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=10, cursor='hand2').pack(pady=5, fill='x')
        
        # AI Button with tooltip
        ai_btn_frame = tk.Frame(btn_frame, bg=ModernTheme.get_card_bg())
        ai_btn_frame.pack(pady=5, fill='x')
        
        ai_btn = tk.Button(ai_btn_frame, text="🤖 Update AI Priorities", command=self.update_ai_priorities,
                          bg=ModernTheme.SECONDARY_BLUE, fg='white', font=('Segoe UI', 10, 'bold'),
                          relief='flat', padx=20, pady=10, cursor='hand2')
        ai_btn.pack(fill='x')
        
        # Tooltip/Help text
        help_text = tk.Label(btn_frame, 
                            text="💡 AI analyzes your tasks and automatically assigns\npriority levels (Critical/High/Normal/Low) based on:\n• Deadline proximity • Urgent keywords • Task age",
                            bg=ModernTheme.get_card_bg(),
                            fg=ModernTheme.get_text_secondary(),
                            font=('Segoe UI', 8),
                            justify='left')
        help_text.pack(pady=(5, 0))

        # Right side - Task list with multi-selection
        tk.Label(right, text="Your Tasks", font=('Segoe UI', 16, 'bold'),
                bg=ModernTheme.get_bg(), fg=ModernTheme.get_text()).pack(pady=10, anchor='w')
        
        # Enable multi-selection
        self.tasks_tree = ttk.Treeview(right, columns=("id","title","deadline","priority","status"), 
                                       show='headings', selectmode='extended')
        self.tasks_tree.heading("id", text="ID")
        self.tasks_tree.heading("title", text="Task")
        self.tasks_tree.heading("deadline", text="Deadline")
        self.tasks_tree.heading("priority", text="Priority")
        self.tasks_tree.heading("status", text="Status")
        self.tasks_tree.column("id", width=50)
        self.tasks_tree.column("title", width=300)
        self.tasks_tree.column("deadline", width=120)
        self.tasks_tree.column("priority", width=100)
        self.tasks_tree.column("status", width=100)
        self.tasks_tree.pack(fill='both', expand=True)

        btn_frame2 = tk.Frame(right, bg=ModernTheme.get_bg())
        btn_frame2.pack(fill='x', pady=10)
        
        tk.Button(btn_frame2, text="✓ Mark Done", command=self.mark_done_ui,
                 bg=ModernTheme.SUCCESS, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame2, text="🗑 Delete Selected", command=self.delete_multiple_tasks_ui,
                 bg=ModernTheme.DANGER, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=5)
        
        tk.Label(btn_frame2, text="💡 Tip: Hold Ctrl to select multiple tasks",
                bg=ModernTheme.get_bg(), fg=ModernTheme.get_text_secondary(),
                font=('Segoe UI', 9, 'italic')).pack(side='left', padx=15)

        self.refresh_tasks()

    def add_task_ui(self):
        t = self.title_entry.get().strip()
        d = self.deadline_picker.get_date().strftime('%Y-%m-%d')
        r = f"{self.hour_spin.get()}:{self.minute_spin.get()}"
        rep = self.repeat_var.get()
        if not t:
            messagebox.showwarning("Validation", "Task title required")
            return
        add_task(t, deadline=d, reminder_time=r, repeat=rep)
        self.title_entry.delete(0,'end')
        self.repeat_var.set("none")
        self.refresh_tasks()
        self.refresh_dashboard()
        self.update_ai_priorities_silent()
        
        # Add XP for creating a task
        gamification.add_xp(5)
        self.update_header_stats()
        
        messagebox.showinfo("Success", "Task added! +5 XP")

    def refresh_tasks(self):
        for r in self.tasks_tree.get_children():
            self.tasks_tree.delete(r)
        for row in get_tasks():
            self.tasks_tree.insert('', 'end', values=row)

    def get_selected_task_id(self):
        sel = self.tasks_tree.selection()
        if not sel:
            return None
        vals = self.tasks_tree.item(sel[0])['values']
        return vals[0]

    def delete_task_ui(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showinfo("Select", "Select a task first")
            return
        delete_task(tid)
        self.refresh_tasks()
        self.refresh_dashboard()
    
    def delete_multiple_tasks_ui(self):
        """Delete multiple selected tasks"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showinfo("Select", "Select at least one task first")
            return
        
        count = len(selected)
        if messagebox.askyesno("Confirm", f"Delete {count} task(s)?"):
            for item in selected:
                task_id = self.tasks_tree.item(item)['values'][0]
                delete_task(task_id)
            self.refresh_tasks()
            self.refresh_dashboard()
            messagebox.showinfo("Success", f"{count} task(s) deleted!")

    def mark_done_ui(self):
        """Mark selected task(s) as done and delete them - supports multi-selection"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showinfo("Select", "Select at least one task first")
            return
        
        # Confirmation dialog
        count = len(selected)
        task_names = []
        for item in selected:
            task_name = self.tasks_tree.item(item)['values'][1]
            task_names.append(task_name)
        
        # Show task names in confirmation
        if count == 1:
            confirm_msg = f"Mark this task as complete and remove it?\n\n✓ {task_names[0]}"
        else:
            confirm_msg = f"Mark {count} tasks as complete and remove them?\n\n"
            for name in task_names[:3]:  # Show first 3
                confirm_msg += f"✓ {name}\n"
            if count > 3:
                confirm_msg += f"... and {count - 3} more"
        
        if not messagebox.askyesno("Confirm Completion", confirm_msg):
            return
        
        total_xp = 0
        level_up_occurred = False
        new_level = 0
        
        for item in selected:
            task_id = self.tasks_tree.item(item)['values'][0]
            # Mark as done and then delete
            mark_task_done(task_id)
            delete_task(task_id)
            xp_result = gamification.record_task_completion()
            total_xp += xp_result['xp_gained']
            if xp_result['level_up']:
                level_up_occurred = True
                new_level = xp_result['level']
        
        self.refresh_tasks()
        self.refresh_dashboard()
        self.check_achievements()
        self.update_header_stats()
        
        msg = f"{count} task(s) completed! +{total_xp} XP"
        if level_up_occurred:
            msg += f"\n🎉 Level Up! You're now level {new_level}!"
        messagebox.showinfo("Success", msg)

    # ---------------- Habits Tab ----------------
    def build_habits_tab(self):
        top = theme_manager.create_card_frame(self.habits_frame)
        top.pack(fill='x', padx=10, pady=10)
        
        # Top row - Add new habit on left, management buttons on right
        input_frame = tk.Frame(top, bg=ModernTheme.get_card_bg())
        input_frame.pack(pady=10, padx=20, fill='x')
        
        # Left side - Add habit
        left_side = tk.Frame(input_frame, bg=ModernTheme.get_card_bg())
        left_side.pack(side='left')
        
        tk.Label(left_side, text="New Habit:", font=('Segoe UI', 11, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text()).pack(side='left', padx=10)
        
        self.habit_entry = tk.Entry(left_side, width=30, bg=ModernTheme.get_input_bg(),
                                    fg=ModernTheme.get_text(), font=('Segoe UI', 10),
                                    insertbackground=ModernTheme.get_text(), relief='solid', bd=2)
        self.habit_entry.pack(side='left', padx=10, ipady=6)
        
        tk.Button(left_side, text="➕ Add", command=self.add_habit_ui,
                 bg=ModernTheme.PRIMARY_BLUE, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=5)
        
        # Right side - Management buttons
        right_side = tk.Frame(input_frame, bg=ModernTheme.get_card_bg())
        right_side.pack(side='right')
        
        tk.Button(right_side, text="✓ Check Today", command=self.check_habit_ui,
                 bg=ModernTheme.SUCCESS, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=5)
        tk.Button(right_side, text="✏️ Edit", command=self.edit_habit_ui,
                 bg=ModernTheme.INFO, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=5)
        tk.Button(right_side, text="🔄 Reset", command=self.reset_habit_streak_ui,
                 bg=ModernTheme.WARNING, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=5)
        tk.Button(right_side, text="🗑 Delete", command=self.delete_habit_ui,
                 bg=ModernTheme.DANGER, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=5)

        list_frame = tk.Frame(self.habits_frame, bg=ModernTheme.get_bg())
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(list_frame, text="Your Habits", font=('Segoe UI', 16, 'bold'),
                bg=ModernTheme.get_bg(), fg=ModernTheme.get_text()).pack(pady=10, anchor='w')
        
        # Info label
        tk.Label(list_frame, text="💡 Select a habit from the table, then use the buttons above to manage it",
                bg=ModernTheme.get_bg(), fg=ModernTheme.get_text_secondary(),
                font=('Segoe UI', 9, 'italic')).pack(pady=(0, 10), anchor='w')
        
        self.habits_list = ttk.Treeview(list_frame, columns=("id","name","streak","last_checked"), show='headings')
        self.habits_list.heading("id", text="ID")
        self.habits_list.heading("name", text="Habit")
        self.habits_list.heading("streak", text="Streak 🔥")
        self.habits_list.heading("last_checked", text="Last Checked")
        self.habits_list.column("id", width=50)
        self.habits_list.column("name", width=300)
        self.habits_list.column("streak", width=100)
        self.habits_list.column("last_checked", width=150)
        self.habits_list.pack(fill='both', expand=True)
        
        self.refresh_habits()

    def add_habit_ui(self):
        name = self.habit_entry.get().strip()
        if not name:
            messagebox.showwarning("Validation","Habit name required")
            return
        add_habit(name)
        self.habit_entry.delete(0,'end')
        self.refresh_habits()
        self.refresh_dashboard()

    def refresh_habits(self):
        for r in self.habits_list.get_children():
            self.habits_list.delete(r)
        for row in get_habits():
            self.habits_list.insert('', 'end', values=row)

    def get_selected_habit_id(self):
        sel = self.habits_list.selection()
        if not sel:
            return None
        return self.habits_list.item(sel[0])['values'][0]

    def check_habit_ui(self):
        hid = self.get_selected_habit_id()
        if not hid:
            messagebox.showinfo("Select", "Select a habit first")
            return
        ok = check_habit(hid)
        if ok:
            xp_result = gamification.record_habit_check()
            self.check_achievements()
            self.update_header_stats()
            msg = f"Habit checked! +{xp_result['xp_gained']} XP"
            if xp_result['level_up']:
                msg += f"\n🎉 Level Up! You're now level {xp_result['level']}!"
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showinfo("Info", "Already checked today")
        self.refresh_habits()
        self.refresh_dashboard()
    
    def delete_habit_ui(self):
        hid = self.get_selected_habit_id()
        if not hid:
            messagebox.showinfo("Select", "Select a habit first")
            return
        if messagebox.askyesno("Confirm", "Delete this habit?"):
            delete_habit(hid)
            self.refresh_habits()
            self.refresh_dashboard()
            messagebox.showinfo("Success", "Habit deleted")
    
    def edit_habit_ui(self):
        """Edit habit name"""
        hid = self.get_selected_habit_id()
        if not hid:
            messagebox.showinfo("Select", "Select a habit first")
            return
        
        # Get current habit name
        sel = self.habits_list.selection()
        current_name = self.habits_list.item(sel[0])['values'][1]
        
        # Create dialog for new name
        dialog = tk.Toplevel(self)
        dialog.title("Edit Habit")
        dialog.geometry("400x150")
        dialog.configure(bg=ModernTheme.get_bg())
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Edit Habit Name", font=('Segoe UI', 12, 'bold'),
                bg=ModernTheme.get_bg(), fg=ModernTheme.get_text()).pack(pady=15)
        
        entry = tk.Entry(dialog, width=40, bg=ModernTheme.get_input_bg(),
                        fg=ModernTheme.get_text(), font=('Segoe UI', 10),
                        insertbackground=ModernTheme.get_text(), relief='solid', bd=2)
        entry.pack(pady=10, padx=20, ipady=8)
        entry.insert(0, current_name)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def save_edit():
            new_name = entry.get().strip()
            if not new_name:
                messagebox.showwarning("Validation", "Habit name cannot be empty")
                return
            update_habit_name(hid, new_name)
            self.refresh_habits()
            self.refresh_dashboard()
            dialog.destroy()
            messagebox.showinfo("Success", "Habit name updated!")
        
        btn_frame = tk.Frame(dialog, bg=ModernTheme.get_bg())
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="💾 Save", command=save_edit,
                 bg=ModernTheme.PRIMARY_BLUE, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy,
                 bg=ModernTheme.get_text_secondary(), fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
        
        entry.bind('<Return>', lambda e: save_edit())
    
    def reset_habit_streak_ui(self):
        """Reset habit streak to 0"""
        hid = self.get_selected_habit_id()
        if not hid:
            messagebox.showinfo("Select", "Select a habit first")
            return
        
        # Get current habit info
        sel = self.habits_list.selection()
        habit_name = self.habits_list.item(sel[0])['values'][1]
        current_streak = self.habits_list.item(sel[0])['values'][2]
        
        if messagebox.askyesno("Confirm Reset", 
                              f"Reset streak for '{habit_name}'?\n\nCurrent streak: {current_streak} days\nThis will set it back to 0."):
            reset_habit_streak(hid)
            self.refresh_habits()
            self.refresh_dashboard()
            messagebox.showinfo("Success", "Habit streak reset to 0")

    # ---------------- Focus Mode Tab ----------------
    def build_focus_tab(self):
        container = tk.Frame(self.focus_frame, bg=ModernTheme.get_bg())
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Timer display
        timer_card = theme_manager.create_card_frame(container)
        timer_card.pack(pady=20)
        
        tk.Label(timer_card, text="🧘 Focus Mode", font=('Segoe UI', 20, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.PRIMARY_BLUE).pack(pady=20)
        
        self.timer_label = tk.Label(timer_card, text="25:00", font=('Segoe UI', 48, 'bold'),
                                    bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text())
        self.timer_label.pack(pady=20)
        
        self.session_label = tk.Label(timer_card, text="Focus Time", font=('Segoe UI', 14),
                                      bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text_secondary())
        self.session_label.pack(pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(timer_card, bg=ModernTheme.get_card_bg())
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="▶ Start", command=self.start_focus,
                 bg=ModernTheme.SUCCESS, fg='white', font=('Segoe UI', 12, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="⏸ Pause", command=self.pause_focus,
                 bg=ModernTheme.WARNING, fg='white', font=('Segoe UI', 12, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="⏹ Reset", command=self.reset_focus,
                 bg=ModernTheme.DANGER, fg='white', font=('Segoe UI', 12, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)
        
        # Start timer update loop
        self.update_focus_timer()
    
    def start_focus(self):
        focus_timer.start()
    
    def pause_focus(self):
        focus_timer.pause()
    
    def reset_focus(self):
        focus_timer.reset()
        self.update_focus_timer()
    
    def update_focus_timer(self):
        """Update focus timer display"""
        self.timer_label.config(text=focus_timer.get_time_string())
        self.session_label.config(text=focus_timer.get_session_type())
        self.after(1000, self.update_focus_timer)
    
    # ---------------- AI Insights Tab ----------------
    def build_ai_tab(self):
        container = tk.Frame(self.ai_frame, bg=ModernTheme.get_bg())
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with refresh button
        header_frame = tk.Frame(container, bg=ModernTheme.get_bg())
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="🤖 AI-Powered Insights", font=('Segoe UI', 20, 'bold'),
                bg=ModernTheme.get_bg(), fg=ModernTheme.PRIMARY_BLUE).pack(side='left')
        
        tk.Button(header_frame, text="🔄 Refresh", command=self.update_ai_insights,
                 bg=ModernTheme.PRIMARY_BLUE, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=8, cursor='hand2').pack(side='right')
        
        # Top stats row - Key metrics
        stats_row = tk.Frame(container, bg=ModernTheme.get_bg())
        stats_row.pack(fill='x', pady=(0, 20))
        
        self.ai_stat_cards = []
        for i in range(4):
            card = theme_manager.create_card_frame(stats_row)
            card.pack(side='left', fill='both', expand=True, padx=5)
            self.ai_stat_cards.append(card)
        
        # Middle section - 2 columns
        middle_frame = tk.Frame(container, bg=ModernTheme.get_bg())
        middle_frame.pack(fill='x', pady=(0, 20))
        
        # Left column - Focus Areas
        left_col = theme_manager.create_card_frame(middle_frame, height=200)
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 10))
        left_col.pack_propagate(False)
        
        tk.Label(left_col, text="🎯 Focus Areas", font=('Segoe UI', 14, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text()).pack(pady=15, padx=20, anchor='w')
        
        self.focus_areas_frame = tk.Frame(left_col, bg=ModernTheme.get_card_bg())
        self.focus_areas_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Right column - Procrastination Analysis
        right_col = theme_manager.create_card_frame(middle_frame, height=200)
        right_col.pack(side='left', fill='both', expand=True, padx=(10, 0))
        right_col.pack_propagate(False)
        
        tk.Label(right_col, text="⚠️ Procrastination Analysis", font=('Segoe UI', 14, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text()).pack(pady=15, padx=20, anchor='w')
        
        self.procrastination_frame = tk.Frame(right_col, bg=ModernTheme.get_card_bg())
        self.procrastination_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Bottom section - AI Recommendations (with scrollable area)
        recommendations_card = theme_manager.create_card_frame(container, height=250)
        recommendations_card.pack(fill='x')
        recommendations_card.pack_propagate(False)
        
        tk.Label(recommendations_card, text="💡 AI Recommendations", font=('Segoe UI', 14, 'bold'),
                bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text()).pack(pady=15, padx=20, anchor='w')
        
        # Create canvas with scrollbar for recommendations
        canvas_frame = tk.Frame(recommendations_card, bg=ModernTheme.get_card_bg())
        canvas_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        canvas = tk.Canvas(canvas_frame, bg=ModernTheme.get_card_bg(), highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.recommendations_frame = tk.Frame(canvas, bg=ModernTheme.get_card_bg())
        
        self.recommendations_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.recommendations_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.update_ai_insights()
    
    def update_ai_insights(self):
        """Update AI insights dashboard"""
        tasks = get_tasks()
        habits = get_habits()
        insights = ai_engine.analyze_productivity_patterns(tasks, habits)
        
        # Update stat cards
        stats = [
            ("📋 Total Tasks", insights['total_tasks'], ModernTheme.PRIMARY_BLUE),
            ("✅ Completed", insights['completed_tasks'], ModernTheme.SUCCESS),
            ("📈 Completion Rate", f"{insights['completion_rate']:.0f}%", ModernTheme.INFO),
            ("⚠️ Overdue", insights['overdue_tasks'], ModernTheme.DANGER if insights['overdue_tasks'] > 0 else ModernTheme.get_text_secondary())
        ]
        
        for i, (label, value, color) in enumerate(stats):
            for widget in self.ai_stat_cards[i].winfo_children():
                widget.destroy()
            
            tk.Label(self.ai_stat_cards[i], text=label, 
                    font=('Segoe UI', 10), bg=ModernTheme.get_card_bg(),
                    fg=ModernTheme.get_text_secondary()).pack(pady=(15, 5))
            tk.Label(self.ai_stat_cards[i], text=str(value),
                    font=('Segoe UI', 24, 'bold'), bg=ModernTheme.get_card_bg(),
                    fg=color).pack(pady=(0, 15))
        
        # Update focus areas
        for widget in self.focus_areas_frame.winfo_children():
            widget.destroy()
        
        if insights['focus_areas']:
            for area in insights['focus_areas']:
                area_frame = tk.Frame(self.focus_areas_frame, bg=ModernTheme.get_card_bg())
                area_frame.pack(fill='x', pady=5)
                tk.Label(area_frame, text="•", font=('Segoe UI', 14, 'bold'),
                        bg=ModernTheme.get_card_bg(), fg=ModernTheme.PRIMARY_BLUE).pack(side='left', padx=(0, 10))
                tk.Label(area_frame, text=area, font=('Segoe UI', 11),
                        bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text(),
                        wraplength=300, justify='left').pack(side='left', fill='x')
        else:
            tk.Label(self.focus_areas_frame, text="No specific focus areas identified",
                    font=('Segoe UI', 10, 'italic'), bg=ModernTheme.get_card_bg(),
                    fg=ModernTheme.get_text_secondary()).pack(pady=20)
        
        # Update procrastination analysis
        for widget in self.procrastination_frame.winfo_children():
            widget.destroy()
        
        score = insights['procrastination_score']
        score_color = ModernTheme.SUCCESS if score < 30 else (ModernTheme.WARNING if score < 60 else ModernTheme.DANGER)
        
        tk.Label(self.procrastination_frame, text=f"{score:.0f}/100",
                font=('Segoe UI', 32, 'bold'), bg=ModernTheme.get_card_bg(),
                fg=score_color).pack(pady=(10, 5))
        
        status = "Low" if score < 30 else ("Moderate" if score < 60 else "High")
        tk.Label(self.procrastination_frame, text=f"{status} Procrastination Level",
                font=('Segoe UI', 11), bg=ModernTheme.get_card_bg(),
                fg=ModernTheme.get_text_secondary()).pack(pady=(0, 10))
        
        # Progress bar
        bar_frame = tk.Frame(self.procrastination_frame, bg=ModernTheme.get_border(), height=10)
        bar_frame.pack(fill='x', padx=20, pady=10)
        bar_fill = tk.Frame(bar_frame, bg=score_color, height=10)
        bar_fill.place(relwidth=score/100, relheight=1)
        
        # Update recommendations
        for widget in self.recommendations_frame.winfo_children():
            widget.destroy()
        
        for i, rec in enumerate(insights['recommendations'], 1):
            rec_frame = tk.Frame(self.recommendations_frame, bg=ModernTheme.get_card_bg())
            rec_frame.pack(fill='x', pady=8)
            
            tk.Label(rec_frame, text=f"{i}.", font=('Segoe UI', 11, 'bold'),
                    bg=ModernTheme.get_card_bg(), fg=ModernTheme.PRIMARY_BLUE).pack(side='left', padx=(0, 10))
            tk.Label(rec_frame, text=rec, font=('Segoe UI', 11),
                    bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text(),
                    wraplength=800, justify='left').pack(side='left', fill='x', expand=True)
    
    # ---------------- Achievements Tab ----------------
    def build_achievements_tab(self):
        container = tk.Frame(self.achievements_frame, bg=ModernTheme.get_bg())
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="🏆 Achievements", font=('Segoe UI', 20, 'bold'),
                bg=ModernTheme.get_bg(), fg=ModernTheme.ACHIEVEMENT_COLOR).pack(pady=20)
        
        # Achievements grid
        canvas = tk.Canvas(container, bg=ModernTheme.get_bg(), highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.get_bg())
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas width changes to update scrollable_frame width
        def on_canvas_configure(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        achievements = gamification.get_achievement_list()
        
        row_frame = None
        for i, ach in enumerate(achievements):
            if i % 3 == 0:
                row_frame = tk.Frame(scrollable_frame, bg=ModernTheme.get_bg())
                row_frame.pack(fill='x', pady=10)
            
            card = theme_manager.create_card_frame(row_frame)
            card.pack(side='left', padx=10, fill='both', expand=True)
            
            # Achievement icon and name
            color = ModernTheme.ACHIEVEMENT_COLOR if ach['unlocked'] else ModernTheme.get_text_secondary()
            
            tk.Label(card, text=ach['name'], font=('Segoe UI', 14, 'bold'),
                    bg=ModernTheme.get_card_bg(), fg=color).pack(pady=10, padx=10)
            
            tk.Label(card, text=ach['description'], font=('Segoe UI', 9),
                    bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text_secondary(),
                    wraplength=200).pack(pady=5, padx=10)
            
            tk.Label(card, text=f"{ach['xp']} XP", font=('Segoe UI', 10, 'bold'),
                    bg=ModernTheme.get_card_bg(), fg=ModernTheme.XP_COLOR).pack(pady=10)
            
            if ach['unlocked']:
                tk.Label(card, text="✓ UNLOCKED", font=('Segoe UI', 9, 'bold'),
                        bg=ModernTheme.get_card_bg(), fg=ModernTheme.SUCCESS).pack(pady=5)
            else:
                tk.Label(card, text="🔒 LOCKED", font=('Segoe UI', 9),
                        bg=ModernTheme.get_card_bg(), fg=ModernTheme.get_text_secondary()).pack(pady=5)

    # ---------------- Helper Methods ----------------
    def update_ai_priorities(self):
        """Update task priorities using AI with notification"""
        self.update_ai_priorities_silent()
        messagebox.showinfo("AI Update", "Task priorities updated using AI!")
    
    def update_ai_priorities_silent(self):
        """Update task priorities using AI without notification"""
        tasks = get_tasks()
        for task in tasks:
            task_id, title, deadline, reminder, repeat, priority, status, *rest = task + (None,)
            if status != 'Done':
                created_at = datetime.now().isoformat()
                score, ai_priority = ai_engine.calculate_smart_priority(title, deadline, created_at)
                update_task_priority(task_id, ai_priority)
        self.refresh_tasks()
    
    def check_achievements(self):
        """Check and display unlocked achievements"""
        tasks = get_tasks()
        habits = get_habits()
        unlocked = gamification.check_achievements(tasks, habits)
        
        if unlocked:
            msg = "🎉 NEW ACHIEVEMENTS UNLOCKED!\n\n"
            for ach_data in unlocked:
                ach = ach_data['achievement']
                msg += f"{ach['name']}\n{ach['desc']}\n+{ach['xp']} XP\n\n"
            messagebox.showinfo("Achievements", msg)


def run_app():
    init_db()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_app()
