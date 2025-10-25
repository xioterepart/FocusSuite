# focus_mode.py
"""
Focus Mode with Pomodoro Timer
===============================
Deep work timer with break intervals
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading
from theme import ModernTheme
from gamification import gamification


class FocusTimer:
    """Pomodoro-style focus timer"""
    
    def __init__(self):
        self.work_duration = 25 * 60  # 25 minutes
        self.break_duration = 5 * 60  # 5 minutes
        self.long_break_duration = 15 * 60  # 15 minutes
        self.sessions_until_long_break = 4
        
        self.current_session = 0
        self.time_remaining = self.work_duration
        self.is_running = False
        self.is_break = False
        self.timer_thread = None
        self.total_focus_time = 0
    
    def start(self):
        """Start the timer"""
        if not self.is_running:
            self.is_running = True
            self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
            self.timer_thread.start()
    
    def pause(self):
        """Pause the timer"""
        self.is_running = False
    
    def reset(self):
        """Reset the timer"""
        self.is_running = False
        self.time_remaining = self.work_duration
        self.is_break = False
    
    def skip(self):
        """Skip to next session"""
        self.time_remaining = 0
    
    def _run_timer(self):
        """Internal timer loop"""
        while self.is_running and self.time_remaining > 0:
            time.sleep(1)
            self.time_remaining -= 1
            
            # Track focus time (only during work sessions)
            if not self.is_break:
                self.total_focus_time += 1
        
        if self.time_remaining == 0:
            self._session_complete()
    
    def _session_complete(self):
        """Handle session completion"""
        if not self.is_break:
            # Work session complete
            self.current_session += 1
            
            # Award XP for focus time
            minutes = self.work_duration // 60
            gamification.record_focus_time(minutes)
            
            # Determine next break type
            if self.current_session % self.sessions_until_long_break == 0:
                self.time_remaining = self.long_break_duration
                self.is_break = True
            else:
                self.time_remaining = self.break_duration
                self.is_break = True
        else:
            # Break complete
            self.time_remaining = self.work_duration
            self.is_break = False
        
        self.is_running = False
    
    def get_time_string(self):
        """Get formatted time string"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_session_type(self):
        """Get current session type"""
        if self.is_break:
            if self.time_remaining > self.break_duration:
                return "Long Break"
            return "Short Break"
        return "Focus Time"
    
    def get_progress(self):
        """Get progress percentage"""
        if self.is_break:
            total = self.long_break_duration if self.time_remaining > self.break_duration else self.break_duration
        else:
            total = self.work_duration
        
        return ((total - self.time_remaining) / total) * 100 if total > 0 else 0


# Singleton instance
focus_timer = FocusTimer()
