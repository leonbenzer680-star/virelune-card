# Setup for Cellular + Laptop (Everywhere Access)

## 🎯 What You'll Get

After setup:
- ✅ Works on home WiFi
- ✅ Works on cellular (4G/5G) anywhere
- ✅ Fully encrypted (private tunnel)
- ✅ No complicated setup
- ✅ Completely free (Tailscale)

---

# STEP 1: Install Tailscale (Free VPN)

Tailscale is a **free VPN that makes your devices find each other automatically**. Think of it as a private internet just for your devices.

## On Your Laptop:

### Windows:
1. Go to: https://tailscale.com/download/windows
2. Download and run installer
3. Click "Connect"
4. Sign in with Google or GitHub
5. Accept (allows connection)

### Mac:
1. Go to: https://tailscale.com/download/mac
2. Download DMG file
3. Install it
4. Click "Connect"
5. Sign in
6. Accept

### Linux:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo systemctl start tailscaled
sudo tailscale up
```

**After login, Tailscale gives your laptop a special address like: `100.123.45.67`**

---

# STEP 2: Install Tailscale on iPhone

1. Open App Store
2. Search: **"Tailscale"**
3. Download and install
4. Open app
5. Tap "Sign in"
6. Sign in with SAME account as laptop
7. Tap "Connect"

**Done!** Your iPhone and laptop are now connected through a private tunnel.

---

# STEP 3: Get Your Laptop's Tailscale Address

On your laptop:

### Windows:
- Open Tailscale (system tray)
- Look for: "Tailscale Address" 
- Should show something like: `100.123.45.67`
- Copy it

### Mac:
- Click Tailscale in menu bar
- Click "Copy Tailscale Address"

### Linux:
```bash
tailscale ip -4
```

**Save this address. You'll use it for your iPhone Shortcut.**

---

# STEP 4: Create iPhone Shortcut (Works Everywhere)

On your iPhone:

1. Open **Shortcuts** app
2. Tap **"+"** (create new)
3. Tap **"Add Action"**
4. Search and add: **"Ask for Text"**
   - Prompt: "Ask your AI:"
   - Variable name: `question`

5. Add action: **"Get Contents of URL"**
   - URL: `http://100.123.45.67:8000/api/ask` 
   - Method: **POST**
   - Headers: 
     ```
     Content-Type: application/json
     ```
   - Request body (JSON):
     ```json
     {"question": "{question}"}
     ```

6. Add action: **"Get Dictionary Value"**
   - Dictionary: (from previous step)
   - Key: `answer`

7. Add action: **"Speak Text"**
   - Text: (from previous step)

8. Name it: **"Ask My AI"**

9. Tap the **three dots** → **Add to Siri**
   - Say phrase: **"Ask my AI"**
   - Done

**Replace `100.123.45.67` with YOUR Tailscale address from Step 3**

---

# STEP 5: Run Your Server

On your laptop:

```bash
cd personal-ai
.\venv\Scripts\Activate.ps1
python main.py
```

You'll see:
```
✓ Server starting at http://localhost:8000
```

**Keep this running!**

---

# STEP 6: Test It

### Test 1: At Home (WiFi)
1. Make sure both are connected to Tailscale
2. On iPhone: Say **"Hey Siri, Ask my AI"**
3. Say a question: **"What time is it?"**
4. Should get response

### Test 2: Outside (Cellular)
1. Turn off WiFi on iPhone
2. Use only cellular (4G/5G)
3. Say: **"Hey Siri, Ask my AI"**
4. Ask a question
5. Should still work!

---

# 🎉 Done!

You now have:
- ✅ **Local access** - Works on home WiFi
- ✅ **Cellular access** - Works on 4G/5G anywhere
- ✅ **Encrypted** - Private tunnel (Tailscale)
- ✅ **Secure** - No exposure to internet
- ✅ **Free** - Tailscale is completely free
- ✅ **Simple** - Just one app to install

---

# 📱 How It Works

```
At Home (WiFi):
iPhone ──WiFi──> Laptop (Server)
                    ↓
                 Claude API
                    ↓
                 Response back

On Cellular (4G/5G):
iPhone ──Cellular──> Tailscale Tunnel ──> Laptop (Server)
                                              ↓
                                           Claude API
                                              ↓
                                          Response back
```

Both routes use the **same Tailscale IP address**. Your Shortcut just works everywhere!

---

# ⚡ Quick Checklist

- [ ] Tailscale installed on laptop
- [ ] Tailscale installed on iPhone
- [ ] Both signed in to SAME account
- [ ] Got laptop's Tailscale address (100.x.x.x)
- [ ] Created iPhone Shortcut with that address
- [ ] Server running on laptop
- [ ] Tested on WiFi
- [ ] Tested on cellular
- [ ] Both work ✅

---

# 🔧 Troubleshooting

### "Can't connect on cellular"
- Make sure Tailscale is running on both devices
- Make sure laptop is on (and connected to internet)
- Restart Tailscale app on iPhone
- Check you used correct Tailscale address

### "Tailscale address keeps changing"
- It shouldn't, but if it does:
- On laptop: Check Tailscale settings
- Enable: "Use Tailscale addresses"

### "Connection times out"
- Laptop might be sleeping
- Keep laptop awake or disable sleep mode
- Check laptop is still running server

### "Works at home but not on cellular"
- Cellular network might be blocking connections
- Try restarting phone
- Try switching WiFi off and on

---

# 💡 Advanced: Multiple Devices

You can use it on **multiple iPhones**:

1. Install Tailscale on each iPhone
2. Sign in with same account
3. Create same Shortcut on each
4. All iPhones can talk to laptop simultaneously

---

# 🔐 Security Notes

**Tailscale is:**
- ✅ Encrypted end-to-end
- ✅ Free to use
- ✅ Private (only your account)
- ✅ No company sniffing
- ✅ Industry standard

Your data travels through an encrypted tunnel. Only your account can access your devices.

---

# 📞 Need Help?

**"Server not responding"**
- Is server running on laptop? Check `python main.py`
- Is Tailscale running? Check Tailscale icon

**"Shortcut not working"**
- Did you use YOUR Tailscale address? (not 100.123.45.67)
- Did you sign in to Tailscale?
- Try restarting iPhone

**"Cellular doesn't work"**
- Turn off WiFi completely
- Make sure you're on 4G/5G
- Check Tailscale is connected on iPhone

---

**That's it! Now you have a personal AI that works everywhere - home, work, traveling, anywhere on the planet. 🚀**
