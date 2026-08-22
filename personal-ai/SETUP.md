# Complete Setup Guide

## ⚠️ IMPORTANT: Do NOT Continue Yet

**Before you do anything, run the environment check to see what's already installed:**

```bash
cd personal-ai
python check_environment.py
```

Then tell me:
- What operating system you're using (Windows/Mac/Linux)
- What the script says is installed
- What the script says needs to be installed

I'll then create the right installer for your system.

---

## The Big Picture

This system works like this:

```
Your iPhone (Siri)
    ↓ (WiFi)
Your Computer (FastAPI Server)
    ↓ (OAuth)
Google Services (Gmail, Calendar, etc.)
    ↓
Claude AI (reasoning engine)
    ↓
Results back to Siri
```

You own everything. Your data stays local. No monthly bills.

---

## What You'll Need to Provide

### 1. Google Account (Gmail, Calendar, etc.)
You probably already have this. Just need to set up API access.

### 2. Claude API Key
Get from: https://console.anthropic.com
- Click "Account" → "API Keys"
- Create a new key
- Keep it secret (we'll store it in `.env`)

### 3. iPhone Shortcut (optional)
Just copy-paste from the Shortcut we'll provide.

---

## General Setup Flow (After Environment Check)

### STEP 1: Create Python Virtual Environment

A "virtual environment" is a separate space where Python can install packages without affecting your system.

**Windows:**
```
cd personal-ai
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```
cd personal-ai
python3 -m venv venv
source venv/bin/activate
```

You'll see `(venv)` at the start of your terminal line when it's activated.

### STEP 2: Install Python Packages

```
pip install -r requirements.txt
```

This downloads all the free libraries we need. Takes 2-5 minutes.

### STEP 3: Copy Environment Template

```
copy .env.example .env
```

Then open `.env` and fill in your values (don't worry, we'll guide you on each one).

### STEP 4: Get Google Credentials

Go to: https://console.cloud.google.com

1. Click the project dropdown (top left)
2. Click "NEW PROJECT"
3. Name it "Personal AI"
4. Wait for it to be created
5. Select it from the dropdown
6. Click the hamburger menu (top left) → "APIs & Services" → "Enabled APIs & services"
7. Click "ENABLE APIS AND SERVICES"
8. Search for and enable:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
   - Google Sheets API
   - People API
9. Click "Credentials" (left sidebar)
10. Click "Create Credentials" → "OAuth 2.0 Client IDs"
11. Choose "Desktop Application"
12. Download the JSON file
13. Save it as: `personal-ai/config/credentials.json`

### STEP 5: Get Claude API Key

1. Go to: https://console.anthropic.com
2. Sign in or create account
3. Click "Account" (top right) → "API Keys"
4. Click "Create Key"
5. Copy the key
6. Paste it into `.env` → `CLAUDE_API_KEY=your-key-here`

### STEP 6: Start the Server

```
python main.py
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### STEP 7: Check the Dashboard

Open your browser and go to:
```
http://localhost:8000
```

You should see a dashboard showing connected services.

### STEP 8: Set Up iPhone Shortcut (Optional)

I'll provide you with a ready-to-use Shortcut. Just:
1. Open Shortcuts app on iPhone
2. Tap the "+" button
3. Tap "Add Action"
4. Tap "Scripting"
5. Tap "Web Request"
6. Follow the configuration we provide

---

## Troubleshooting Common Issues

### "Python not found" or "Command not recognized"
- On Windows: Make sure Python is installed and added to PATH
- Run `python --version` to check
- If not installed, download from python.org

### "pip: command not found"
- Python 3 should include pip
- Try: `python -m pip --version`
- If nothing works, reinstall Python with "Add Python to PATH" checked

### "Module not found" when running server
- Make sure virtual environment is activated
- You should see `(venv)` in your terminal
- If not, run the activation command again

### "Connection refused" when accessing iPhone
- Make sure your iPhone is on the same WiFi as your computer
- Get your computer's IP: On Windows, run `ipconfig` and look for "IPv4 Address"
- In Shortcut, use that IP instead of `localhost`

### "Google credentials error"
- Make sure `credentials.json` is in `personal-ai/config/`
- Make sure APIs are enabled in Google Cloud Console
- Try deleting and re-downloading the credentials

---

## Security Checklist

- [ ] `.env` file created and added to `.gitignore`
- [ ] `credentials.json` never committed to Git
- [ ] `CLAUDE_API_KEY` in `.env`, not in code
- [ ] `ENCRYPTION_KEY` generated and in `.env`
- [ ] OAuth tokens stored locally only

---

## What's in Each Directory

```
config/
  ├── settings.json          # Configuration (safe to commit)
  ├── credentials.json       # Google OAuth (DO NOT COMMIT)
  └── tokens.json           # Access tokens (DO NOT COMMIT)

connectors/
  ├── gmail/                # Email connector
  ├── calendar/             # Calendar connector
  ├── contacts/             # Contacts connector
  └── [etc for other services]

security/
  ├── oauth.py              # Handles Google login
  ├── crypto.py             # Encrypts tokens
  └── permissions.py        # Checks what you can do

dashboard/
  ├── app.py                # Web server
  ├── static/               # HTML/CSS/JS
  └── templates/            # HTML templates

logs/
  └── activity.log          # What the AI did

tests/
  └── test_*.py             # Automated tests
```

---

## Next Steps

1. **Run the environment check** (if you haven't already)
2. **Tell me what you found**
3. **I'll create the right installer for your system**
4. **Follow the setup guide**
5. **We'll connect services one by one**

Do NOT try to install Python yourself or download random packages. Wait for my guidance.

---

## Getting Help

If something breaks:
1. Check the troubleshooting section above
2. Look at the logs in `logs/activity.log`
3. Tell me what error you got and what you were trying to do

The system is designed to be user-friendly and forgiving. Most issues have simple fixes.

---

**Ready? Go run `python check_environment.py` and let me know what you find! 🚀**
