# Gmail + Amazon Catchall Setup Guide

**Author:** Leo Benzer / Virelune Labs  
**Script:** `catchall.py`  
**Purpose:** Download Gmail attachments, check Amazon prices, automate checkout

---

## Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install google-auth google-auth-oauthlib google-api-python-client playwright
playwright install chromium

# 2. Set up Gmail OAuth (see Step 1 below)
# 3. Run one-time Amazon login (see Step 2 below)
# 4. Use the functions in your code!
```

---

## Step 1: Gmail OAuth Setup (One-time)

### 1a. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **"Create Project"**
3. Name it: `virelune-catchall` (or any name you prefer)
4. Click **Create**
5. Wait 30 seconds for the project to initialize

### 1b. Enable Gmail API

1. In the search bar at the top, search for **"Gmail API"**
2. Click **Gmail API** from results
3. Click **Enable**
4. Wait for it to enable (blue checkmark appears)

### 1c. Create OAuth Credentials

1. On the left sidebar, click **Credentials**
2. Click **+ Create Credentials** at the top
3. Choose **OAuth client ID**
4. If prompted, click **Configure OAuth consent screen** first:
   - Select **External** (personal use)
   - Click **Create**
   - Fill in:
     - **App name:** `Virelune Catchall`
     - **User support email:** your email
     - **Developer contact:** your email
   - Click **Save and Continue**
   - Click **Add or Remove Scopes**
   - Search for and add `Gmail API (.../auth/gmail.readonly)`
   - Click **Update**
   - Scroll to bottom, click **Save and Continue**
   - Click **Back to Dashboard**

5. Now go back to **Credentials** (left sidebar)
6. Click **+ Create Credentials** → **OAuth client ID**
7. Select **Desktop application**
8. Click **Create**
9. Click **Download** (or the download icon) → **Download JSON**
10. Save the file as `gmail_credentials.json` in:
    ```
    ~/.virelune_catchall/gmail_credentials.json
    ```

    On **Mac/Linux:**
    ```bash
    mkdir -p ~/.virelune_catchall
    # Move the downloaded file to that folder
    mv ~/Downloads/client_secret_*.json ~/.virelune_catchall/gmail_credentials.json
    ```

    On **Windows:**
    ```
    C:\Users\YourUsername\.virelune_catchall\gmail_credentials.json
    ```

### 1d. First-Time Gmail Login

Run this in Python to trigger the one-time OAuth login:

```python
from catchall import get_gmail_service
service = get_gmail_service()
print("✓ Gmail authenticated!")
```

A browser window will pop up asking you to log in to Google. Sign in with your account. The token is saved automatically for future use.

---

## Step 2: Amazon Session Setup (One-time)

### 2a. Trigger Amazon Login

```python
from catchall import amazon_login_once
amazon_login_once()
```

A browser window opens. **Log in to Amazon manually** with your account. The session/cookies are saved automatically.

### 2b. Verify

After login, you should see:
```
✓ Amazon session saved!
  Location: ~/.virelune_catchall/amazon_session.json
```

---

## Step 3: Use the Functions

### Download Gmail Attachments

```python
from catchall import download_gmail_attachment

# Download all attachments
attachments = download_gmail_attachment()

# Download attachments from specific sender
attachments = download_gmail_attachment(query="from:boss@example.com")

# Download attachments with keyword in subject
attachments = download_gmail_attachment(query="subject:invoice")

# Files saved to: ~/.virelune_catchall/downloads/
for att in attachments:
    print(f"✓ {att['filename']} from {att['sender']}")
    print(f"  Saved to: {att['path']}")
```

### Check Amazon Price

```python
from catchall import amazon_check_price

# Get ASIN from Amazon URL: amazon.com/dp/B000ABC123
# The ASIN is "B000ABC123"

price_info = amazon_check_price("B000ABC123")
if price_info:
    print(f"Product: {price_info['title']}")
    print(f"Price: {price_info['price']}")
    print(f"URL: {price_info['url']}")
```

### Automate Amazon Checkout

```python
from catchall import amazon_buy_now

# Add item to cart and go to checkout
amazon_buy_now("B000ABC123", quantity=2)

# Browser opens. Complete payment manually.
# Close browser when done.
```

---

## File Locations

All data stored in `~/.virelune_catchall/`:

| File | Purpose |
|------|---------|
| `gmail_credentials.json` | Gmail OAuth credentials (YOU create this) |
| `gmail_token.json` | Gmail access token (auto-created after first login) |
| `amazon_session.json` | Amazon cookies/session (auto-created after login) |
| `downloads/` | Downloaded Gmail attachments |

---

## Troubleshooting

### "Gmail credentials not found"
→ Make sure you saved `gmail_credentials.json` to `~/.virelune_catchall/` (Step 1d)

### "No Amazon session found"
→ Run `amazon_login_once()` first to create a session (Step 2)

### Browser doesn't open for Amazon login
→ Make sure Playwright is installed: `playwright install chromium`

### Gmail token expired
→ The script auto-refreshes it. Just run `get_gmail_service()` again.

### Amazon session expired
→ Run `amazon_login_once()` again to refresh

---

## Advanced: Custom Gmail Queries

Gmail search filters you can use:

```python
# By sender
download_gmail_attachment(query="from:sender@example.com")

# By date (attachments from last week)
download_gmail_attachment(query="newer_than:7d")

# By label
download_gmail_attachment(query="label:Work")

# Combine
download_gmail_attachment(query="from:boss@example.com newer_than:7d")

# Exclude
download_gmail_attachment(query="from:spam@example.com -has:attachment")
```

Full Gmail search syntax: [Google Support](https://support.google.com/mail/answer/7190)

---

## FAQ

**Q: Do I need to log in every time?**  
A: No. After the one-time login, tokens/sessions are cached and reused.

**Q: Is my password stored?**  
A: No. Only OAuth tokens and Amazon cookies are saved. Passwords are never stored.

**Q: Can I use this in automation (scripts, cron jobs)?**  
A: Yes. Once tokens are cached, all functions work without browser interaction.

**Q: What if I want to use a different Gmail account?**  
A: Delete `~/.virelune_catchall/gmail_token.json` and run `get_gmail_service()` again.

**Q: Can I use this in Google Colab?**  
A: Yes, but Amazon login requires file persistence (session won't work if Colab session restarts).

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Set up Gmail OAuth
3. ✅ Set up Amazon session
4. ✅ Import functions and use them!

Happy automating! 🚀
