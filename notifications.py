# notifications.py
import threading
import time
from datetime import datetime
from plyer import notification
from database import get_conn

def reminder_loop(stop_event):
    while not stop_event.is_set():
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, title, reminder_time FROM tasks WHERE reminder_time IS NOT NULL AND status!='Done'")
        rows = c.fetchall()
        conn.close()
        for tid, title, reminder_time in rows:
            if not reminder_time:
                continue
            # allow reminders stored as "HH:MM" or "YYYY-MM-DD HH:MM"
            if len(reminder_time.strip()) == 5:  # "HH:MM"
                # compare HH:MM and today
                if datetime.now().strftime("%H:%M") == reminder_time:
                    notification.notify(title="FocusSuite Reminder", message=title, timeout=8)
            else:
                if reminder_time == now:
                    notification.notify(title="FocusSuite Reminder", message=title, timeout=8)
        # sleep 30s
        stop_event.wait(30)

def start_reminder_thread():
    stop_event = threading.Event()
    t = threading.Thread(target=reminder_loop, args=(stop_event,), daemon=True)
    t.start()
    return stop_event
