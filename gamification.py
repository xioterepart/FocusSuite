# gamification.py
"""
Gamification System for FocusSuite
===================================
Viral app features including:
- XP and Leveling system
- Achievement badges
- Streak protection
- Daily challenges
- Leaderboard (local)
"""

import json
import os
from datetime import datetime, date
from database import get_conn

GAMIFICATION_DB = "gamification.json"

class GamificationSystem:
    """
    Manages all gamification features
    """
    
    ACHIEVEMENTS = {
        'first_task': {'name': '🎯 First Step', 'desc': 'Complete your first task', 'xp': 50},
        'task_master_10': {'name': '📋 Task Master', 'desc': 'Complete 10 tasks', 'xp': 100},
        'task_master_50': {'name': '🏆 Task Champion', 'desc': 'Complete 50 tasks', 'xp': 500},
        'task_master_100': {'name': '👑 Task Legend', 'desc': 'Complete 100 tasks', 'xp': 1000},
        
        'streak_3': {'name': '🔥 On Fire', 'desc': '3-day habit streak', 'xp': 75},
        'streak_7': {'name': '⚡ Week Warrior', 'desc': '7-day habit streak', 'xp': 150},
        'streak_30': {'name': '💎 Diamond Streak', 'desc': '30-day habit streak', 'xp': 500},
        'streak_100': {'name': '🌟 Century Club', 'desc': '100-day habit streak', 'xp': 2000},
        
        'early_bird': {'name': '🌅 Early Bird', 'desc': 'Complete a task before 8 AM', 'xp': 100},
        'night_owl': {'name': '🦉 Night Owl', 'desc': 'Complete a task after 10 PM', 'xp': 100},
        'speed_demon': {'name': '⚡ Speed Demon', 'desc': 'Complete 5 tasks in one day', 'xp': 200},
        'consistency': {'name': '📅 Consistency King', 'desc': 'Use app 7 days in a row', 'xp': 300},
        
        'habit_collector': {'name': '🎨 Habit Collector', 'desc': 'Track 5 different habits', 'xp': 150},
        'perfect_day': {'name': '✨ Perfect Day', 'desc': 'Complete all tasks and habits in one day', 'xp': 500},
        'comeback': {'name': '💪 Comeback Kid', 'desc': 'Complete 3 overdue tasks', 'xp': 200},
        'focus_master': {'name': '🧘 Focus Master', 'desc': 'Spend 2 hours in focus mode', 'xp': 300},
    }
    
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self):
        """Load gamification data from JSON file"""
        if os.path.exists(GAMIFICATION_DB):
            try:
                with open(GAMIFICATION_DB, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default data structure
        return {
            'xp': 0,
            'level': 1,
            'achievements': [],
            'streak_freezes': 3,
            'daily_challenge': None,
            'challenge_completed': False,
            'last_active_date': None,
            'consecutive_days': 0,
            'total_tasks_completed': 0,
            'total_focus_time': 0,
            'stats': {
                'tasks_completed_today': 0,
                'habits_checked_today': 0,
                'last_reset_date': str(date.today())
            }
        }
    
    def _save_data(self):
        """Save gamification data to JSON file"""
        with open(GAMIFICATION_DB, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_xp(self, amount, reason=""):
        """Add XP and check for level up"""
        old_level = self.data['level']
        self.data['xp'] += amount
        
        # Level up formula: XP needed = level * 100
        new_level = 1
        xp_remaining = self.data['xp']
        while xp_remaining >= new_level * 100:
            xp_remaining -= new_level * 100
            new_level += 1
        
        self.data['level'] = new_level
        self._save_data()
        
        level_up = new_level > old_level
        return {
            'xp_gained': amount,
            'total_xp': self.data['xp'],
            'level': new_level,
            'level_up': level_up,
            'reason': reason
        }
    
    def get_xp_for_next_level(self):
        """Calculate XP needed for next level"""
        current_level = self.data['level']
        xp_for_current = sum(i * 100 for i in range(1, current_level))
        xp_for_next = sum(i * 100 for i in range(1, current_level + 1))
        
        current_xp = self.data['xp']
        xp_into_level = current_xp - xp_for_current
        xp_needed = current_level * 100
        
        return {
            'current_xp': xp_into_level,
            'xp_needed': xp_needed,
            'percentage': (xp_into_level / xp_needed) * 100 if xp_needed > 0 else 0
        }
    
    def unlock_achievement(self, achievement_id):
        """Unlock an achievement and award XP"""
        if achievement_id in self.data['achievements']:
            return None  # Already unlocked
        
        if achievement_id not in self.ACHIEVEMENTS:
            return None  # Invalid achievement
        
        achievement = self.ACHIEVEMENTS[achievement_id]
        self.data['achievements'].append(achievement_id)
        xp_result = self.add_xp(achievement['xp'], f"Achievement: {achievement['name']}")
        self._save_data()
        
        return {
            'achievement': achievement,
            'xp_result': xp_result
        }
    
    def check_achievements(self, tasks, habits):
        """Check and unlock achievements based on current progress"""
        unlocked = []
        
        # Task-based achievements
        completed_tasks = [t for t in tasks if t[6] == 'Done']
        total_completed = len(completed_tasks)
        
        if total_completed >= 1 and 'first_task' not in self.data['achievements']:
            result = self.unlock_achievement('first_task')
            if result:
                unlocked.append(result)
        
        if total_completed >= 10 and 'task_master_10' not in self.data['achievements']:
            result = self.unlock_achievement('task_master_10')
            if result:
                unlocked.append(result)
        
        if total_completed >= 50 and 'task_master_50' not in self.data['achievements']:
            result = self.unlock_achievement('task_master_50')
            if result:
                unlocked.append(result)
        
        if total_completed >= 100 and 'task_master_100' not in self.data['achievements']:
            result = self.unlock_achievement('task_master_100')
            if result:
                unlocked.append(result)
        
        # Habit streak achievements
        if habits:
            max_streak = max(h[2] for h in habits)  # streak at index 2
            
            if max_streak >= 3 and 'streak_3' not in self.data['achievements']:
                result = self.unlock_achievement('streak_3')
                if result:
                    unlocked.append(result)
            
            if max_streak >= 7 and 'streak_7' not in self.data['achievements']:
                result = self.unlock_achievement('streak_7')
                if result:
                    unlocked.append(result)
            
            if max_streak >= 30 and 'streak_30' not in self.data['achievements']:
                result = self.unlock_achievement('streak_30')
                if result:
                    unlocked.append(result)
            
            if max_streak >= 100 and 'streak_100' not in self.data['achievements']:
                result = self.unlock_achievement('streak_100')
                if result:
                    unlocked.append(result)
            
            # Habit collector
            if len(habits) >= 5 and 'habit_collector' not in self.data['achievements']:
                result = self.unlock_achievement('habit_collector')
                if result:
                    unlocked.append(result)
        
        # Consistency achievement
        if self.data['consecutive_days'] >= 7 and 'consistency' not in self.data['achievements']:
            result = self.unlock_achievement('consistency')
            if result:
                unlocked.append(result)
        
        return unlocked
    
    def use_streak_freeze(self, habit_id):
        """Use a streak freeze to protect a habit"""
        if self.data['streak_freezes'] <= 0:
            return False
        
        self.data['streak_freezes'] -= 1
        self._save_data()
        return True
    
    def earn_streak_freeze(self):
        """Earn a streak freeze (reward for achievements)"""
        self.data['streak_freezes'] += 1
        self._save_data()
    
    def update_daily_stats(self):
        """Reset daily stats if it's a new day"""
        today = str(date.today())
        last_reset = self.data['stats'].get('last_reset_date')
        
        if last_reset != today:
            # New day - reset daily stats
            self.data['stats'] = {
                'tasks_completed_today': 0,
                'habits_checked_today': 0,
                'last_reset_date': today
            }
            self.data['challenge_completed'] = False
            
            # Update consecutive days
            last_active = self.data.get('last_active_date')
            if last_active:
                try:
                    last_date = datetime.fromisoformat(last_active).date()
                    if (date.today() - last_date).days == 1:
                        self.data['consecutive_days'] += 1
                    else:
                        self.data['consecutive_days'] = 1
                except:
                    self.data['consecutive_days'] = 1
            else:
                self.data['consecutive_days'] = 1
            
            self.data['last_active_date'] = today
            self._save_data()
    
    def record_task_completion(self):
        """Record a task completion for daily stats"""
        self.update_daily_stats()
        self.data['stats']['tasks_completed_today'] += 1
        self.data['total_tasks_completed'] += 1
        self._save_data()
        
        # Award XP
        return self.add_xp(10, "Task completed")
    
    def record_habit_check(self):
        """Record a habit check for daily stats"""
        self.update_daily_stats()
        self.data['stats']['habits_checked_today'] += 1
        self._save_data()
        
        # Award XP
        return self.add_xp(15, "Habit checked")
    
    def record_focus_time(self, minutes):
        """Record time spent in focus mode"""
        self.data['total_focus_time'] += minutes
        self._save_data()
        
        # Award XP based on focus time
        xp = int(minutes / 5)  # 1 XP per 5 minutes
        return self.add_xp(xp, f"Focus time: {minutes} min")
    
    def get_stats(self):
        """Get current gamification stats"""
        return {
            'level': self.data['level'],
            'xp': self.data['xp'],
            'xp_progress': self.get_xp_for_next_level(),
            'achievements_unlocked': len(self.data['achievements']),
            'total_achievements': len(self.ACHIEVEMENTS),
            'streak_freezes': self.data['streak_freezes'],
            'consecutive_days': self.data['consecutive_days'],
            'total_tasks_completed': self.data['total_tasks_completed'],
            'total_focus_time': self.data['total_focus_time'],
            'daily_stats': self.data['stats']
        }
    
    def get_achievement_list(self):
        """Get list of all achievements with unlock status"""
        achievements = []
        for aid, ach in self.ACHIEVEMENTS.items():
            achievements.append({
                'id': aid,
                'name': ach['name'],
                'description': ach['desc'],
                'xp': ach['xp'],
                'unlocked': aid in self.data['achievements']
            })
        return achievements


# Singleton instance
gamification = GamificationSystem()
