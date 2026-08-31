#!/usr/bin/env python3
"""
QUICKSTART — Run this after setup to verify everything works.

1. First, complete SETUP.md (Gmail OAuth + Amazon login)
2. Then run: python QUICKSTART.py
"""

from catchall import (
    download_gmail_attachment,
    amazon_check_price,
    get_gmail_service,
    GMAIL_TOKEN_PATH,
    AMAZON_SESSION_PATH,
)

print("=" * 70)
print("VIRELUNE CATCHALL — Verification Check")
print("=" * 70)
print()

# Check 1: Gmail
print("1️⃣  Checking Gmail setup...")
if GMAIL_TOKEN_PATH.exists():
    try:
        service = get_gmail_service()
        print("   ✓ Gmail authenticated")
    except Exception as e:
        print(f"   ✗ Gmail error: {e}")
        print("   → Run setup in SETUP.md, Step 1")
else:
    print("   ✗ Gmail token not found")
    print("   → Run setup in SETUP.md, Step 1")

print()

# Check 2: Amazon
print("2️⃣  Checking Amazon setup...")
if AMAZON_SESSION_PATH.exists():
    print("   ✓ Amazon session saved")
else:
    print("   ✗ Amazon session not found")
    print("   → Run setup in SETUP.md, Step 2")

print()
print("=" * 70)

# Try to download attachments
print("\n3️⃣  Testing attachment download...")
try:
    attachments = download_gmail_attachment(query="has:attachment", )
    if attachments:
        print(f"   ✓ Found {len(attachments)} attachment(s)")
    else:
        print("   ℹ️  No attachments found (normal if inbox is empty)")
except Exception as e:
    print(f"   ✗ Error: {e}")

print()
print("=" * 70)
print("✓ Verification complete!")
print()
print("Next: Use functions in your code")
print("  from catchall import download_gmail_attachment, amazon_check_price")
print()
