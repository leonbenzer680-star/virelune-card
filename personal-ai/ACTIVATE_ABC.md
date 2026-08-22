# Activate A→B→C: Claude, Gmail, Drive

## ✅ What's Ready

### A: Claude AI ✅
- Fully integrated
- Conversation history
- Real AI responses
- Just need API key

### B: Gmail ✅
- OAuth ready
- Read emails
- Search emails
- Parse content

### C: Drive ✅
- OAuth ready
- Search files
- Read documents
- Get recent files

---

# 🚀 Setup (15 Minutes)

## STEP 1: Get Claude API Key

1. Go to: https://console.anthropic.com
2. Click "Account" → "API Keys"
3. Click "Create Key"
4. Copy your key
5. Open `personal-ai/.env`
6. Find line: `CLAUDE_API_KEY=sk-ant-REPLACE_WITH_YOUR_KEY`
7. Replace with your actual key
8. Save

**Test it:**
```bash
cd personal-ai
.\venv\Scripts\Activate.ps1
python main.py
```

Your server will now respond with real Claude responses instead of placeholders.

---

## STEP 2: Get Google OAuth Credentials

Go to: https://console.cloud.google.com

### 1. Create Project
- Click project dropdown (top left)
- Click "NEW PROJECT"
- Name: "Personal AI"
- Create

### 2. Enable APIs
- Click hamburger menu (top left)
- Click "APIs & Services"
- Click "Enable APIs and Services"
- Search for and enable:
  - Gmail API
  - Google Drive API
  - Google Docs API
  - Google Sheets API

### 3. Create OAuth Credentials
- Click "Credentials" (left sidebar)
- Click "Create Credentials" → "OAuth 2.0 Client IDs"
- Choose "Desktop Application"
- Click "Create"
- Click the download icon (right side)
- Save as: `personal-ai/config/credentials.json`

**Done!** You now have credentials.

---

## STEP 3: Activate Services

With server running, call these endpoints:

### Activate Claude (Automatic)
Claude activates automatically when you ask it a question.

Test:
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is your name?"}'
```

Should respond with real Claude answer!

### Activate Gmail
```bash
curl -X POST http://localhost:8000/api/gmail/auth
```

Browser will pop up → Sign in with Google → Approve → Done

### Activate Drive
```bash
curl -X POST http://localhost:8000/api/drive/auth
```

Will automatically use Gmail credentials.

---

## STEP 4: Test Everything

### Test Claude
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Summarize what you can do"}'
```

### Test Gmail (Get Recent Emails)
```bash
curl http://localhost:8000/api/gmail/recent
```

Should return: List of your recent emails

### Test Gmail (Search)
```bash
curl "http://localhost:8000/api/gmail/search?q=important"
```

Should return: Emails matching "important"

### Test Drive (Search Files)
```bash
curl "http://localhost:8000/api/drive/search?q=budget"
```

Should return: Files containing "budget"

### Test Drive (Recent Files)
```bash
curl http://localhost:8000/api/drive/recent
```

Should return: Your 10 most recently modified files

---

# 🎯 Use from iPhone Shortcut

Your Shortcut already works with Claude!

Say:
```
"Hey Siri, Ask my AI [question]"
```

Examples:
```
"Hey Siri, Ask my AI what's in my Gmail"
→ Claude reads your email and summarizes

"Hey Siri, Ask my AI what files do I have"
→ Claude searches your Drive

"Hey Siri, Ask my AI find Q4 budget"
→ Claude finds relevant files
```

---

# 📊 How They Work Together

```
iPhone: "Ask my AI what's in my Gmail"
         ↓
Claude:  Receives question
         ↓
Claude:  Recognizes it's about Gmail
         ↓
Gmail:   Fetches your recent emails
         ↓
Claude:  Reads emails and summarizes
         ↓
Claude:  "You have 3 important emails..."
         ↓
Siri:    Speaks response
```

---

# 🔐 Permissions

Each service requires minimal permissions:

**Claude:**
- No permissions (just API key)

**Gmail:**
- Read emails ✓
- Read labels ✓
- Modify labels ✓
- Send emails ✗ (not enabled)

**Drive:**
- Read files ✓
- Read documents ✓
- Read spreadsheets ✓
- Delete files ✗ (not enabled)

All safe, selective permissions.

---

# 💡 What You Can Do Now

### With Claude Only:
```
"What time is it?"
"What can you do?"
"Explain machine learning"
"Tell me a joke"
```

### With Claude + Gmail:
```
"What's in my Gmail?"
"Do I have any emails from John?"
"Summarize my emails"
"Search for emails about the project"
```

### With Claude + Drive:
```
"What files do I have?"
"Find my budget spreadsheet"
"Search for documents about Q4"
"What are my recent files?"
```

### With Claude + Both:
```
"What's in my Gmail and what files do I have?"
"Find important emails and the related files"
"Check my calendar and emails"
```

---

# 🚨 Troubleshooting

### "CLAUDE_API_KEY not set"
- Edit `.env`
- Add your Claude key
- Restart server

### "Gmail authentication failed"
- Make sure `credentials.json` is in `config/` folder
- Make sure Gmail API is enabled in Google Cloud Console
- Try authenticating again

### "Drive authentication failed"
- Gmail must be authenticated first
- Then Drive will automatically work

### "Email search returns nothing"
- Gmail might not have permissions
- Try simpler search (just "test")
- Make sure you're authenticated

### "Files not found"
- Drive might not have permissions
- Make sure Google Drive API is enabled
- Check you're searching in the right Drive

---

# 📝 API Reference

### Ask Claude
```
POST /api/ask
Body: {"question": "your question"}
Response: {"answer": "Claude's response"}
```

### Gmail Auth
```
POST /api/gmail/auth
Opens browser for OAuth
Response: {"status": "success"}
```

### Get Recent Emails
```
GET /api/gmail/recent
Response: {"emails": [...], "count": 5}
```

### Search Emails
```
GET /api/gmail/search?q=query
Response: {"emails": [...], "count": N}
```

### Drive Auth
```
POST /api/drive/auth
Uses Gmail credentials
Response: {"status": "success"}
```

### Search Drive
```
GET /api/drive/search?q=query
Response: {"files": [...], "count": N}
```

### Get Recent Files
```
GET /api/drive/recent
Response: {"files": [...], "count": 10}
```

---

# ✨ You Now Have

✅ **A: Claude AI** - Real AI reasoning with conversation memory
✅ **B: Gmail** - Read, search, summarize your emails
✅ **C: Drive** - Search files, read documents

All working together, all free (except Claude API cost).

---

**Everything is built. Just add your API keys and authenticate! 🚀**
