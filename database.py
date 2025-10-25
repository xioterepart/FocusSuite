# database.py
import sqlite3
from datetime import datetime, date, timedelta

DB_PATH = "focussuite.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deadline TEXT,
            reminder_time TEXT,
            repeat TEXT DEFAULT 'none',     -- none|daily|weekly
            priority TEXT DEFAULT 'Normal',
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            last_checked TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ---- TASK CRUD ----
def add_task(title, deadline=None, reminder_time=None, repeat='none'):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (title, deadline, reminder_time, repeat) VALUES (?, ?, ?, ?)",
        (title, deadline, reminder_time, repeat)
    )
    conn.commit()
    conn.close()

def get_tasks():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, title, deadline, reminder_time, repeat, priority, status FROM tasks ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_tasks_by_date(target_date_iso):
    """Return tasks whose deadline == target_date_iso (YYYY-MM-DD)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, title, deadline, reminder_time, repeat, priority, status FROM tasks WHERE deadline=?", (target_date_iso,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_task(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def mark_task_done(task_id):
    """
    Mark a task done. If it has a repeating rule, create the next occurrence.
    """
    conn = get_conn()
    c = conn.cursor()
    # read task
    c.execute("SELECT title, deadline, reminder_time, repeat FROM tasks WHERE id=?", (task_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    title, deadline, reminder_time, repeat = row
    # mark done
    c.execute("UPDATE tasks SET status='Done' WHERE id=?", (task_id,))
    conn.commit()

    # If repeating, create next occurrence (simple)
    if repeat and repeat.lower() in ('daily', 'weekly'):
        # compute next deadline
        try:
            if deadline:
                d = datetime.fromisoformat(deadline).date()
            else:
                d = date.today()
        except Exception:
            # try to parse just date
            try:
                d = datetime.strptime(deadline, "%Y-%m-%d").date()
            except Exception:
                d = date.today()

        if repeat.lower() == 'daily':
            next_d = d + timedelta(days=1)
        else:
            next_d = d + timedelta(days=7)

        next_deadline = next_d.isoformat()
        # create new task with same title, reminder shifted if present (attempt to preserve time)
        new_reminder = None
        if reminder_time:
            # if reminder is YYYY-MM-DD HH:MM or HH:MM, try preserve HH:MM
            parts = reminder_time.split()
            time_part = parts[-1] if len(parts) > 1 else parts[0]
            # new_reminder = next_deadline + " " + time_part
            new_reminder = f"{next_deadline} {time_part}" if len(parts) > 1 else f"{next_deadline} {time_part}"

        c.execute("INSERT INTO tasks (title, deadline, reminder_time, repeat) VALUES (?, ?, ?, ?)",
                  (title, next_deadline, new_reminder, repeat))
        conn.commit()
    conn.close()

# ---- HABIT CRUD ----
def add_habit(name):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO habits (name, streak, last_checked) VALUES (?, 0, NULL)", (name,))
    conn.commit()
    conn.close()

def get_habits():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, streak, last_checked FROM habits ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def check_habit(habit_id):
    """
    Check a habit for today. Updates streak if appropriate.
    Returns True if checked successfully, False if already checked today.
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT streak, last_checked FROM habits WHERE id=?", (habit_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    
    streak, last_checked = row
    today = date.today().isoformat()
    
    # Check if already checked today
    if last_checked == today:
        conn.close()
        return False
    
    # Update streak logic
    if last_checked:
        try:
            last_date = datetime.fromisoformat(last_checked).date()
            days_diff = (date.today() - last_date).days
            
            if days_diff == 1:
                # Consecutive day - increment streak
                streak += 1
            elif days_diff > 1:
                # Streak broken - reset to 1
                streak = 1
            else:
                # Same day (shouldn't happen due to check above)
                streak = streak
        except:
            streak = 1
    else:
        # First time checking
        streak = 1
    
    c.execute("UPDATE habits SET streak=?, last_checked=? WHERE id=?", (streak, today, habit_id))
    conn.commit()
    conn.close()
    return True

def delete_habit(habit_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM habits WHERE id=?", (habit_id,))
    conn.commit()
    conn.close()

def update_habit_name(habit_id, new_name):
    """Update habit name"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE habits SET name=? WHERE id=?", (new_name, habit_id))
    conn.commit()
    conn.close()

def reset_habit_streak(habit_id):
    """Reset habit streak to 0"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE habits SET streak=0, last_checked=NULL WHERE id=?", (habit_id,))
    conn.commit()
    conn.close()

def update_task_priority(task_id, priority):
    """Update task priority (used by AI engine)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE tasks SET priority=? WHERE id=?", (priority, task_id))
    conn.commit()
    conn.close()
