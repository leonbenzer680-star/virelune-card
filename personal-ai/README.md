# Personal AI Assistant - Free-First Edition

A modular, locally-running AI assistant that integrates with your Gmail, Google services, iPhone, and browser. **Zero cost. OAuth-based security. Your data stays with you.**

## Architecture Overview

```
personal-ai/
├── config/              # Configuration & API key management
├── connectors/          # Service integrations
│   ├── gmail/          # Email
│   ├── calendar/       # Google Calendar
│   ├── contacts/       # Google Contacts
│   ├── drive/          # Google Drive
│   ├── sheets/         # Google Sheets
│   ├── docs/           # Google Docs
│   ├── maps/           # Google Maps
│   ├── browser/        # Web automation
│   ├── iphone/         # iPhone Shortcuts
│   ├── notifications/  # Notification delivery
│   └── voice/          # Voice I/O
├── security/           # OAuth tokens, encryption
├── dashboard/          # Web UI (local)
├── logs/               # Activity logs
└── tests/              # Automated tests
```

## What Can Be Done For FREE

### ✓ Fully Free (No Cost, No Limits)

- **Gmail** - Read, search, draft, label using OAuth 2.0
- **Google Calendar** - Read, create, modify events
- **Google Contacts** - Search, retrieve contact data
- **Google Drive** - Search, read, organize files
- **Google Docs** - Read, create, edit documents
- **Google Sheets** - Read, write, add rows
- **Browser Automation** - Playwright + free browser (Chrome/Firefox)
- **iPhone Shortcuts** - Native integration via HTTP requests
- **Voice** - Apple's native speech-to-text/text-to-speech (free on device)
- **Notifications** - iPhone native + Email
- **Local Server** - FastAPI running on your machine
- **Dashboard** - Simple HTML/CSS dashboard

### ⚠️ Limited Free Tier

- **Google Maps API** - Limited free requests (~$200/month free credit)
  - Supported: Business search, directions, geocoding
  - NOT supported: Buying Maps API for phone calling

### ✗ Cannot Be Done For Free

- **Business Phone Calling** - Would require paid Twilio or similar
  - **Alternative**: Use Google Search's AI Mode for calling (Google handles the calls)
- **SMS Notifications** - All SMS services are paid
  - **Alternative**: Email notifications + iPhone native notifications

## What This System Will Do

### Email (Gmail)
```
"Hey Siri, ask my AI what's important in my emails"
→ AI reads your Gmail
→ Summarizes important emails
→ Siri speaks the results
```

### Calendar
```
"Hey Siri, ask my AI what I have tomorrow"
→ Checks your Google Calendar
→ Lists all events and conflicts
```

### Files (Drive)
```
"Hey Siri, ask my AI to search my files for 'Q4 budget'"
→ Searches Google Drive
→ Returns file summaries
```

### Web Search
```
"Hey Siri, ask my AI to find plumbers near me"
→ Uses browser automation to search
→ Returns options with prices/reviews
```

### Smart Integration
```
"Hey Siri, ask my AI to create a meeting with John at 2pm Tuesday"
→ Checks calendar for conflicts
→ Creates event
→ Asks for confirmation before saving
```

## Getting Started

### STEP 1: Check Your System

```bash
python check_environment.py
```

This will tell you what's installed and what needs to be installed.

### STEP 2: Install Python Dependencies

(Skip if you already have these)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### STEP 3: Connect Google Services

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project called "Personal AI"
3. Enable these APIs:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
   - Google Sheets API
   - People API (for Contacts)
   - Maps API (optional)

4. Create OAuth 2.0 credentials (Desktop Application)
5. Download credentials as JSON
6. Copy to `config/credentials.json`

### STEP 4: Start the Server

```bash
python main.py
```

The dashboard will open at `http://localhost:8000`

### STEP 5: Set Up iPhone Shortcut

1. Open the Shortcuts app on iPhone
2. Create New → Add Action → Web Request
3. URL: `http://[your-computer-ip]:8000/api/ask`
4. Method: POST
5. Body: `{"question": "Dictation Input"}`

Now you can say: "Hey Siri, ask my AI what's in my Gmail"

## Security & Privacy

### OAuth Only - No Passwords
- Never stores your Gmail, Google, or Apple passwords
- Uses OAuth 2.0 for secure access
- Tokens refresh automatically

### Local First
- Runs on your Windows/Mac/Linux computer
- Data never leaves your machine (except to Google APIs with your permission)
- No cloud server, no third-party access

### Selective Permissions
- Read-only by default
- Requires explicit confirmation for:
  - Sending emails
  - Deleting anything
  - Canceling appointments
  - Making changes

### Environment Variables
- Store API keys in `.env` file
- Never commit secrets to Git
- `.env` is in `.gitignore`

## Cost Control

The system has built-in cost detection:

1. Tracks all API usage
2. Alerts before using any paid service
3. Prevents unauthorized charges
4. Shows estimated costs for any paid operation

**Default: FREE ONLY**

Any paid API requires explicit user approval.

## Dashboard Features

When you visit `http://localhost:8000`, you'll see:

```
CONNECTED SERVICES
━━━━━━━━━━━━━━━━━━━━
Gmail       ✓ CONNECTED
Calendar    ✓ CONNECTED
Contacts    ✓ CONNECTED
Drive       ✓ CONNECTED
Sheets      ✓ CONNECTED
Docs        ✓ CONNECTED
Maps        ○ DISCONNECTED
iPhone      ✓ CONNECTED

AI PROVIDER
━━━━━━━━━━━━━━━━━━━━
Claude API  ✓ READY

COST
━━━━━━━━━━━━━━━━━━━━
Target:     $0
Current:    $0
Status:     FREE ✓

RECENT ACTIVITY
━━━━━━━━━━━━━━━━━━━━
14:32  Read 3 emails from workspace
14:15  Created calendar event
14:01  Searched files in Drive
13:45  iPhone Shortcut connected
```

## Project Structure

```
personal-ai/
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Template for environment variables
├── check_environment.py       # Environment detection script
├── config/
│   ├── settings.json         # Default settings
│   └── credentials.json      # Google OAuth (generated)
├── connectors/
│   ├── __init__.py
│   ├── gmail/
│   │   ├── connector.py      # Gmail API wrapper
│   │   └── test_gmail.py     # Tests
│   ├── calendar/
│   ├── contacts/
│   ├── drive/
│   ├── sheets/
│   ├── docs/
│   ├── maps/
│   ├── browser/
│   ├── iphone/
│   └── notifications/
├── security/
│   ├── oauth.py              # OAuth 2.0 handler
│   ├── crypto.py             # Token encryption
│   └── permissions.py        # Permission checks
├── dashboard/
│   ├── app.py                # FastAPI server
│   ├── static/
│   │   ├── index.html        # Dashboard UI
│   │   └── style.css
│   └── templates/
├── logs/
│   └── activity.log          # Action log
└── tests/
    ├── test_connectors.py
    └── test_security.py
```

## Development Plan

### Phase 1: Foundation (This Phase)
- [x] Project structure
- [x] Environment check script
- [ ] Wait for your approval

### Phase 2: Core Infrastructure
- [ ] FastAPI server
- [ ] OAuth handler
- [ ] Configuration system
- [ ] Basic dashboard

### Phase 3: Gmail Integration
- [ ] Read emails
- [ ] Search emails
- [ ] Draft replies
- [ ] Label management

### Phase 4: Calendar & Contacts
- [ ] Google Calendar integration
- [ ] Google Contacts integration
- [ ] Event management

### Phase 5: Drive & Docs/Sheets
- [ ] Google Drive search
- [ ] Document reading
- [ ] Spreadsheet operations

### Phase 6: Browser Automation
- [ ] Playwright setup
- [ ] Web scraping
- [ ] Form filling

### Phase 7: iPhone Integration
- [ ] Shortcut handler
- [ ] Voice input/output
- [ ] Notifications

### Phase 8: Testing & Polish
- [ ] Full test suite
- [ ] Windows installer
- [ ] Documentation

## Common Questions

**Q: Is this safe?**
A: Yes. OAuth means your passwords stay with Google/Apple. Tokens are encrypted locally. You control all permissions.

**Q: Can I use this on my phone?**
A: The server runs on your computer. iPhone uses Shortcuts to send requests to the server. This works on home WiFi or over the internet with proper security.

**Q: What if my computer is off?**
A: The assistant only works when the computer is running. Consider leaving it on as a small server.

**Q: Can I extend this with other services?**
A: Yes. The modular design makes it easy to add new connectors (Slack, Notion, GitHub, etc.).

**Q: How much will this cost?**
A: $0 if you stay within free tier limits. Google gives free credits, and Maps/Gmail have high free limits.

## Next Steps

1. **Run the environment check:**
   ```bash
   python check_environment.py
   ```

2. **Report back with:**
   - What's already installed
   - What needs to be installed
   - Whether you're on Windows, Mac, or Linux

3. **I will then:**
   - Create the installer for your platform
   - Set up the core FastAPI server
   - Build the OAuth configuration system
   - Start with Gmail integration

**Do not install anything yet. Just run the environment check and wait for approval.**

---

Built with ❤️ for privacy-first personal AI.
**Zero subscriptions. Zero passwords. Zero cloud lock-in.**
