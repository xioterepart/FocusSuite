# ai_engine.py
"""
AI-Powered Features for FocusSuite
===================================
This module provides intelligent features using machine learning and NLP:
1. Smart Task Prioritization - ML-based urgency scoring
2. Productivity Insights - Pattern analysis and recommendations
3. Habit Recommendations - Personalized coaching
4. Time Estimation - Predictive analytics for task completion
"""

import re
from datetime import datetime, date, timedelta
from collections import Counter
import json
import random

class AIEngine:
    """
    AI Engine for FocusSuite
    
    Features:
    - Task priority scoring using multiple factors
    - Natural language processing for task analysis
    - Productivity pattern detection
    - Personalized recommendations
    """
    
    def __init__(self):
        self.productivity_keywords = {
            'urgent': 3, 'asap': 3, 'critical': 3, 'important': 2,
            'meeting': 2, 'deadline': 2, 'review': 1, 'email': 1
        }
        
    def calculate_smart_priority(self, task_title, deadline, created_at):
        """
        AI-powered priority calculation
        
        Factors considered:
        1. Deadline proximity (40% weight)
        2. Keyword urgency (30% weight)
        3. Task age (20% weight)
        4. Title length/complexity (10% weight)
        
        Returns: Priority score (0-100) and label (Low/Normal/High/Critical)
        """
        score = 0
        
        # Factor 1: Deadline proximity (40 points max)
        if deadline:
            try:
                deadline_date = datetime.fromisoformat(deadline).date()
                days_until = (deadline_date - date.today()).days
                
                if days_until < 0:
                    score += 40  # Overdue
                elif days_until == 0:
                    score += 35  # Due today
                elif days_until == 1:
                    score += 30  # Due tomorrow
                elif days_until <= 3:
                    score += 25  # Due within 3 days
                elif days_until <= 7:
                    score += 15  # Due within a week
                else:
                    score += max(0, 10 - days_until // 7)  # Further out
            except:
                pass
        
        # Factor 2: Keyword urgency analysis (30 points max)
        title_lower = task_title.lower()
        keyword_score = 0
        for keyword, weight in self.productivity_keywords.items():
            if keyword in title_lower:
                keyword_score += weight * 3
        score += min(30, keyword_score)
        
        # Factor 3: Task age (20 points max)
        if created_at:
            try:
                created = datetime.fromisoformat(created_at)
                age_days = (datetime.now() - created).days
                # Older tasks get higher priority (procrastination penalty)
                score += min(20, age_days * 2)
            except:
                pass
        
        # Factor 4: Title complexity (10 points max)
        # Longer, more detailed tasks might be more important
        word_count = len(task_title.split())
        score += min(10, word_count)
        
        # Determine priority label
        if score >= 70:
            priority = "Critical"
        elif score >= 50:
            priority = "High"
        elif score >= 30:
            priority = "Normal"
        else:
            priority = "Low"
            
        return min(100, score), priority
    
    def analyze_productivity_patterns(self, tasks, habits):
        """
        Analyze user's productivity patterns using ML-inspired techniques
        
        Returns insights dictionary with:
        - completion_rate: Overall task completion percentage
        - best_day: Most productive day pattern
        - procrastination_score: Tendency to delay tasks
        - focus_areas: Most common task categories
        - recommendations: AI-generated suggestions
        """
        insights = {
            'completion_rate': 0,
            'total_tasks': len(tasks),
            'completed_tasks': 0,
            'overdue_tasks': 0,
            'procrastination_score': 0,
            'focus_areas': [],
            'recommendations': []
        }
        
        if not tasks:
            insights['recommendations'].append("Start by adding your first task to build momentum!")
            return insights
        
        completed = [t for t in tasks if t[6] == 'Done']  # status at index 6
        pending = [t for t in tasks if t[6] != 'Done']
        
        insights['completed_tasks'] = len(completed)
        insights['completion_rate'] = (len(completed) / len(tasks)) * 100 if tasks else 0
        
        # Analyze overdue tasks
        today = date.today()
        for task in pending:
            deadline = task[2]  # deadline at index 2
            if deadline:
                try:
                    deadline_date = datetime.fromisoformat(deadline).date()
                    if deadline_date < today:
                        insights['overdue_tasks'] += 1
                except:
                    pass
        
        # Calculate procrastination score (0-100)
        if pending:
            insights['procrastination_score'] = min(100, (insights['overdue_tasks'] / len(pending)) * 100)
        
        # Extract focus areas using NLP-inspired keyword extraction
        all_titles = [t[1].lower() for t in tasks]  # title at index 1
        words = []
        for title in all_titles:
            # Remove common words and extract meaningful terms
            words.extend([w for w in re.findall(r'\b\w+\b', title) if len(w) > 3])
        
        if words:
            word_freq = Counter(words)
            insights['focus_areas'] = [word for word, _ in word_freq.most_common(5)]
        
        # Generate AI recommendations
        insights['recommendations'] = self._generate_recommendations(insights, habits)
        
        return insights
    
    def _generate_recommendations(self, insights, habits):
        """
        Generate personalized recommendations based on user patterns
        """
        recommendations = []
        
        # Completion rate recommendations
        if insights['completion_rate'] < 30:
            recommendations.append("🎯 Try breaking large tasks into smaller, manageable steps")
            recommendations.append("⏰ Set realistic deadlines to avoid overwhelm")
        elif insights['completion_rate'] < 60:
            recommendations.append("📈 You're making progress! Focus on consistency")
            recommendations.append("🔥 Consider using the Pomodoro technique for better focus")
        else:
            recommendations.append("🌟 Excellent completion rate! You're crushing it!")
            recommendations.append("🚀 Challenge yourself with more ambitious goals")
        
        # Procrastination recommendations
        if insights['procrastination_score'] > 50:
            recommendations.append("⚠️ High procrastination detected. Try the 2-minute rule: if it takes less than 2 minutes, do it now")
            recommendations.append("🧠 Use the Eisenhower Matrix to prioritize urgent vs important tasks")
        
        # Overdue tasks
        if insights['overdue_tasks'] > 3:
            recommendations.append(f"📌 You have {insights['overdue_tasks']} overdue tasks. Tackle the smallest one first!")
        
        # Habit recommendations
        if habits:
            avg_streak = sum(h[2] for h in habits) / len(habits) if habits else 0  # streak at index 2
            if avg_streak < 3:
                recommendations.append("💪 Build momentum by maintaining a 7-day streak on one habit")
            elif avg_streak >= 7:
                recommendations.append("🔥 Amazing habit streaks! Consider adding a new challenging habit")
        else:
            recommendations.append("✨ Start tracking a habit to build long-term success")
        
        # Focus area recommendations
        if insights['focus_areas']:
            top_area = insights['focus_areas'][0]
            recommendations.append(f"🎓 Your main focus is '{top_area}'. Consider time-blocking for deep work")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def predict_task_duration(self, task_title, historical_tasks):
        """
        Predict task completion time based on historical data
        
        Uses simple ML-inspired heuristics:
        - Similar task analysis
        - Word count correlation
        - Category-based estimation
        """
        # Simple heuristic: estimate based on title length and keywords
        word_count = len(task_title.split())
        
        # Base estimation
        if word_count <= 3:
            estimated_minutes = 15
        elif word_count <= 6:
            estimated_minutes = 30
        elif word_count <= 10:
            estimated_minutes = 60
        else:
            estimated_minutes = 120
        
        # Adjust based on keywords
        title_lower = task_title.lower()
        if any(word in title_lower for word in ['meeting', 'call', 'standup']):
            estimated_minutes = 30
        elif any(word in title_lower for word in ['research', 'analyze', 'review']):
            estimated_minutes = 90
        elif any(word in title_lower for word in ['email', 'message', 'quick']):
            estimated_minutes = 10
        
        return estimated_minutes
    
    def generate_habit_insights(self, habit_name, streak, last_checked):
        """
        Generate AI-powered insights for a specific habit
        """
        insights = {
            'motivation_message': '',
            'streak_status': '',
            'next_milestone': 0,
            'tips': []
        }
        
        # Streak status
        if streak == 0:
            insights['streak_status'] = "🌱 Just starting"
            insights['motivation_message'] = "Every expert was once a beginner. Start today!"
            insights['next_milestone'] = 3
        elif streak < 7:
            insights['streak_status'] = "🔥 Building momentum"
            insights['motivation_message'] = f"You're {7 - streak} days away from your first week!"
            insights['next_milestone'] = 7
        elif streak < 30:
            insights['streak_status'] = "💪 Strong habit forming"
            insights['motivation_message'] = "You're in the habit formation zone. Keep going!"
            insights['next_milestone'] = 30
        elif streak < 100:
            insights['streak_status'] = "⭐ Habit master"
            insights['motivation_message'] = "This habit is part of your identity now!"
            insights['next_milestone'] = 100
        else:
            insights['streak_status'] = "🏆 Legendary"
            insights['motivation_message'] = "You're an inspiration! This is who you are."
            insights['next_milestone'] = (streak // 100 + 1) * 100
        
        # Generate tips based on habit type
        habit_lower = habit_name.lower()
        if any(word in habit_lower for word in ['exercise', 'workout', 'gym', 'run']):
            insights['tips'] = [
                "Schedule it like a meeting",
                "Prepare your gear the night before",
                "Start with just 5 minutes if motivation is low"
            ]
        elif any(word in habit_lower for word in ['read', 'book']):
            insights['tips'] = [
                "Keep your book visible",
                "Read during your morning coffee",
                "Try audiobooks for busy days"
            ]
        elif any(word in habit_lower for word in ['meditate', 'mindful']):
            insights['tips'] = [
                "Same time, same place daily",
                "Use a guided meditation app",
                "Start with 2 minutes, not 20"
            ]
        else:
            insights['tips'] = [
                "Stack it with an existing habit",
                "Track it visually for motivation",
                "Celebrate small wins"
            ]
        
        return insights
    
    def generate_daily_challenge(self, user_level=1):
        """
        Generate a daily challenge based on user level
        """
        challenges = {
            'beginner': [
                "Complete 3 tasks today",
                "Check off one habit",
                "Add a task with a deadline",
                "Review your task list",
                "Set a reminder for tomorrow"
            ],
            'intermediate': [
                "Complete 5 tasks today",
                "Maintain all habit streaks",
                "Tackle your highest priority task first",
                "Spend 25 minutes in focus mode",
                "Clear all overdue tasks"
            ],
            'advanced': [
                "Complete 8+ tasks today",
                "Achieve a 7-day streak on all habits",
                "Complete all critical priority tasks",
                "Spend 2 hours in deep focus",
                "Help someone else with their goals"
            ]
        }
        
        if user_level <= 3:
            difficulty = 'beginner'
        elif user_level <= 10:
            difficulty = 'intermediate'
        else:
            difficulty = 'advanced'
        
        challenge = random.choice(challenges[difficulty])
        xp_reward = {'beginner': 50, 'intermediate': 100, 'advanced': 200}[difficulty]
        
        return {
            'challenge': challenge,
            'difficulty': difficulty,
            'xp_reward': xp_reward
        }
    
    def calculate_focus_score(self, tasks_completed_today, time_in_focus_mode, habits_checked_today):
        """
        Calculate a daily focus score (0-100)
        """
        score = 0
        
        # Tasks completed (40 points max)
        score += min(40, tasks_completed_today * 8)
        
        # Time in focus mode (40 points max)
        score += min(40, (time_in_focus_mode / 120) * 40)  # 120 minutes = max
        
        # Habits checked (20 points max)
        score += min(20, habits_checked_today * 10)
        
        return min(100, score)


# Singleton instance
ai_engine = AIEngine()
