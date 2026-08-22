# Complete Setup - Laptop + Cellular (Everything Works)

**Total time: 15 minutes**

---

# 📊 What You're Setting Up

| Device | Connection | Works |
|--------|-----------|-------|
| Laptop | Local | ✅ |
| iPhone at Home | WiFi | ✅ |
| iPhone Anywhere | Cellular 4G/5G | ✅ |

---

# 🚀 THE FAST TRACK (5 Minutes)

## Part A: Laptop Setup

### 1. Install Dependencies
```
cd personal-ai
powershell -ExecutionPolicy Bypass -File install.ps1
```

### 2. Edit .env File
Open `personal-ai/.env` and replace:
```
CLAUDE_API_KEY=sk-ant-REPLACE_WITH_YOUR_KEY
```

Get key from: https://console.anthropic.com

### 3. Start Server
```
.\venv\Scripts\Activate.ps1
python main.py
```

**Leave this running!**

---

## Part B: Install Tailscale (Free VPN)

This lets your iPhone connect from anywhere.

### 1. Download Tailscale
Windows: https://tailscale.com/download/windows

### 2. Install and Run
- Run installer
- Click "Connect"
- Sign in (Google or GitHub)

### 3. Get Your Address
- Open Tailscale (system tray)
- Look for address like: `100.123.45.67`
- **Copy it** (you'll need it for iPhone)

---

## Part C: iPhone Setup

### 1. Install Tailscale
- App Store → Search "Tailscale"
- Download and install
- Open app, tap "Sign in"
- Sign in with **SAME account** as laptop
- Tap "Connect"

### 2. Create Shortcut
Open **Shortcuts** app:

1. **"+"** → Create new
2. **"Add Action"** → **"Ask for Text"**
   - Prompt: "Ask your AI:"
3. **"Add Action"** → **"Get Contents of URL"**
   - URL: `http://100.123.45.67:8000/api/ask`
   - Method: `POST`
   - Headers: `Content-Type: application/json`
   - Body: `{"question": "{ask_for_text}"}`
4. **"Add Action"** → **"Speak Text"**
   - Text: Get the `answer` field
5. Name it: "Ask My AI"
6. **three dots** → **"Add to Siri"** → Say: "Ask my AI"

**⚠️ Important:** Replace `100.123.45.67` with YOUR Tailscale address!

---

## Part D: Test It

### Test 1: Home WiFi
1. Both on same WiFi
2. Say: "Hey Siri, Ask my AI"
3. Ask: "What's the time?"
4. Should respond ✅

### Test 2: Cellular
1. Turn OFF WiFi on iPhone
2. Use 4G/5G only
3. Say: "Hey Siri, Ask my AI"
4. Ask: "What am I"
5. Should still respond ✅

---

# ✅ Done!

You now have a personal AI that works:
- On your laptop
- On your iPhone at home
- On your iPhone anywhere on cellular
- Completely encrypted
- Completely free (except Claude API)

---

# 🎯 How to Use

Say on iPhone:
```
"Hey Siri, Ask my AI [your question]"
```

Examples:
```
"Hey Siri, Ask my AI what's in my Gmail"
"Hey Siri, Ask my AI what do I have today"
"Hey Siri, Ask my AI find coffee near me"
"Hey Siri, Ask my AI summarize my emails"
```

---

# 📱 iPhone Shortcut Template (Copy-Paste)

Replace `100.123.45.67` with YOUR Tailscale address:

```
URL: http://100.123.45.67:8000/api/ask
Method: POST
Headers: 
  Content-Type: application/json
Body (raw JSON):
  {
    "question": "{ask_text}"
  }
Then speak the response
```

---

# 🔑 Getting Your Tailscale Address

**Windows:**
1. Click Tailscale icon (system tray)
2. Look for line with: `100.x.x.x`
3. That's your address

**On Shortcut URL line, put:**
```
http://YOUR_ADDRESS:8000/api/ask
```

---

# 🆘 Common Issues

| Problem | Fix |
|---------|-----|
| Shortcut not working | Check Tailscale is running on both devices |
| Can't connect on cellular | Restart Tailscale app on iPhone |
| Server not responding | Make sure `python main.py` is running |
| Wrong Tailscale address | Get address from Tailscale app, not guessing |
| Laptop sleeping | Keep it awake or disable sleep mode |

---

# 📝 Checklist

- [ ] Server installed and running
- [ ] Tailscale installed on laptop
- [ ] Tailscale installed on iPhone
- [ ] Both signed into SAME Tailscale account
- [ ] Got laptop's Tailscale address
- [ ] Created iPhone Shortcut with address
- [ ] Claude API key in .env
- [ ] Tested on WiFi ✅
- [ ] Tested on cellular ✅
- [ ] Works everywhere ✅

---

# 🎉 You Have:

✅ **Personal AI Assistant**
- Runs on your laptop
- Accesses Gmail, Calendar, Drive
- Uses Claude for reasoning
- Costs ~$0.50-$5/month

✅ **iPhone Integration**
- Works on WiFi at home
- Works on cellular anywhere
- Uses Siri for voice
- Completely encrypted

✅ **Privacy First**
- No cloud storage
- No passwords stored
- No tracking
- All data stays with you

✅ **Free Setup**
- Python (free)
- Tailscale (free)
- Claude (paid, but cheap)
- Google APIs (free tier)

---

# 🚀 Next: Connect Services

Once this is working, you can add:
1. **Gmail** - Read emails, search
2. **Calendar** - See events, create meetings
3. **Drive** - Search files, read documents
4. **Contacts** - Find contact info
5. **Maps** - Search nearby places

Each takes ~15 minutes to set up.

---

**Ready? Follow the Fast Track above! You'll have everything working in 15 minutes. 🚀**
