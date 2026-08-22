# Get Started in 3 Minutes

## 1️⃣ Install

**Windows:**
```
powershell -ExecutionPolicy Bypass -File install.ps1
```

**Mac/Linux:**
```
bash install.sh
```

Done! It installs everything automatically.

---

## 2️⃣ Add Your Claude API Key

1. Go to: https://console.anthropic.com
2. Click "Account" → "API Keys" → "Create Key"
3. Copy the key
4. Open `.env` file (in the personal-ai folder)
5. Replace `REPLACE_WITH_YOUR_KEY` with your actual key
6. Save the file

---

## 3️⃣ Start the Server

**Windows:**
```
.\venv\Scripts\Activate.ps1
python main.py
```

**Mac/Linux:**
```
source venv/bin/activate
python main.py
```

You'll see:
```
✓ Server starting at http://localhost:8000
```

Open your browser to: **http://localhost:8000**

---

## 🎉 Done!

You now have:
- ✓ Running AI server
- ✓ Dashboard showing status
- ✓ Ready for iPhone Shortcuts
- ✓ Cost: $0 + Claude API (~$0.50-$5/month)

---

## Next: Connect Services

To add Gmail, Calendar, Drive, etc., you'll need Google OAuth credentials.

That takes ~10 more minutes but gives you full integration with your Google account.

Ready for that? I'll guide you through it.

---

## Troubleshooting

**"Python not found"**
- Install from python.org
- Make sure "Add to PATH" is checked during install

**"Module not found"**
- Make sure virtual environment is activated
- You should see `(venv)` before your terminal prompt

**"Port 8000 already in use"**
- Edit `.env` and change `SERVER_PORT` to 8001
- Restart the server

**Server won't start**
- Check that `.env` file exists
- Make sure `CLAUDE_API_KEY` has a value (even a placeholder)

---

That's it! You have a working AI server running locally on your computer. 🚀
