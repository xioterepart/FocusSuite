# 🚀 Quick Setup Guide

## First Time Setup

### 1. Clone the Repository
```bash
git clone https://github.com/xioterepart/FocusSuite.git
cd FocusSuite
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

## What Happens on First Run?

The app will automatically create:
- `focussuite.db` - SQLite database for tasks and habits
- `gamification.json` - Your XP, level, and achievements data

These files are in `.gitignore` and won't be tracked by Git.

## Troubleshooting

### NumPy Version Error
If you see `AttributeError: _ARRAY_API not found`:
```bash
pip uninstall numpy -y
pip install -r requirements.txt
```

### Module Not Found
Make sure you're in the project directory and virtual environment is activated:
```bash
cd FocusSuite
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Database Errors
Delete the database files to reset:
```bash
# Windows
del focussuite.db gamification.json

# Linux/Mac
rm focussuite.db gamification.json
```

Then restart the app.

## Need Help?

- 📖 Check the [README.md](README.md) for full documentation
- 🐛 Report issues on [GitHub Issues](https://github.com/xioterepart/FocusSuite/issues)
- 💬 Contact: elboudadilina2@example.com

---

**Happy Productivity! 🎯**
