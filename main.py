# main.py
from database import init_db
from gui import App
from notifications import start_reminder_thread

if __name__ == "__main__":
    init_db()
    stop_event = start_reminder_thread()
    app = App()
    try:
        app.mainloop()
    finally:
        stop_event.set()
