"""
CATCH-ALL SCRIPT — Gmail Attachment Fetch + Amazon Price Check & Checkout
Built for: Leo Benzer / Virelune Labs

Works identically in Claude Code or local Python — plain Python, no platform-specific code.
Handles Gmail OAuth, attachment downloads, Amazon login, price checking, and checkout flows.
"""

import os
import json
import pickle
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.oauthlib.flow import InstalledAppFlow
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from playwright.sync_api import sync_playwright, Page, BrowserContext
import base64


# ==============================================================================
# PATHS & CONFIG
# ==============================================================================

CONFIG_DIR = Path.home() / ".virelune_catchall"
CONFIG_DIR.mkdir(exist_ok=True)

GMAIL_TOKEN_PATH = CONFIG_DIR / "gmail_token.json"
GMAIL_SECRETS_PATH = CONFIG_DIR / "gmail_credentials.json"
AMAZON_SESSION_PATH = CONFIG_DIR / "amazon_session.json"
DOWNLOADS_DIR = CONFIG_DIR / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ==============================================================================
# GMAIL OAUTH & ATTACHMENT HANDLING
# ==============================================================================

def get_gmail_service():
    """Authenticate with Gmail API. One-time setup, then cached token reuse."""
    creds = None

    # Load cached token if it exists
    if GMAIL_TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN_PATH), GMAIL_SCOPES)

    # If no token or token expired, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not GMAIL_SECRETS_PATH.exists():
                raise FileNotFoundError(
                    f"Gmail OAuth credentials not found at {GMAIL_SECRETS_PATH}\n"
                    "Download from Google Cloud Console (see SETUP.md)"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(GMAIL_SECRETS_PATH), GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next time
        with open(GMAIL_TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def download_gmail_attachment(
    query: str = "has:attachment", save_dir: Optional[Path] = None
) -> List[Dict]:
    """
    Download attachments from Gmail matching query.
    query: Gmail search filter (e.g., "from:sender@example.com has:attachment")
    save_dir: Where to save files (default: DOWNLOADS_DIR)
    """
    if save_dir is None:
        save_dir = DOWNLOADS_DIR

    save_dir.mkdir(exist_ok=True)
    service = get_gmail_service()
    results = []

    try:
        # Search for messages
        messages = service.users().messages().list(userId="me", q=query).execute()
        message_list = messages.get("messages", [])

        if not message_list:
            print(f"No messages found for query: {query}")
            return results

        for msg in message_list:
            msg_id = msg["id"]
            msg_data = service.users().messages().get(userId="me", id=msg_id).execute()
            headers = msg_data["payload"].get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")

            # Extract attachments
            parts = msg_data["payload"].get("parts", [])
            for part in parts:
                if part["filename"]:
                    attachment_id = part["id"]
                    filename = part["filename"]

                    attachment_data = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId="me", messageId=msg_id, id=attachment_id)
                        .execute()
                    )

                    data = attachment_data.get("data", "")
                    if data:
                        file_data = base64.urlsafe_b64decode(data)
                        file_path = save_dir / filename

                        with open(file_path, "wb") as f:
                            f.write(file_data)

                        results.append(
                            {
                                "filename": filename,
                                "path": str(file_path),
                                "subject": subject,
                                "sender": sender,
                                "downloaded_at": datetime.now().isoformat(),
                            }
                        )
                        print(f"✓ Downloaded: {filename} from {sender}")

    except HttpError as error:
        print(f"An error occurred: {error}")

    return results


# ==============================================================================
# AMAZON LOGIN & SESSION HANDLING
# ==============================================================================

def amazon_login_once():
    """
    One-time Amazon login flow. Opens browser for manual login, saves session.
    Run this ONCE, then amazon_check_price() and amazon_buy_now() work offline.
    """
    print("🔐 Starting Amazon login flow...")
    print("   A browser window will open. Log in to Amazon manually.")
    print("   Session will be saved for future use.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to Amazon
        page.goto("https://www.amazon.com")

        # Wait for user to log in (check if 'Account & Lists' text appears, indicating login)
        try:
            page.wait_for_selector('[data-feature-id="nav-signin-base"]', timeout=60000)
            page.wait_for_load_state("networkidle")
        except:
            pass  # User might have logged in already; continue

        # Save cookies and local storage to session file
        cookies = context.cookies()
        storage = context.storage_state()

        session_data = {
            "cookies": cookies,
            "storage": storage,
            "saved_at": datetime.now().isoformat(),
        }

        with open(AMAZON_SESSION_PATH, "w") as f:
            json.dump(session_data, f, indent=2)

        print("\n✓ Amazon session saved!")
        print(f"  Location: {AMAZON_SESSION_PATH}")

        browser.close()


def load_amazon_session() -> Optional[Dict]:
    """Load saved Amazon session from disk."""
    if not AMAZON_SESSION_PATH.exists():
        print(
            "⚠️  No Amazon session found. Run amazon_login_once() first to create one."
        )
        return None

    with open(AMAZON_SESSION_PATH, "r") as f:
        return json.load(f)


def amazon_check_price(asin: str) -> Optional[Dict]:
    """
    Check Amazon product price using saved session.
    asin: Amazon Standard Identification Number (e.g., "B000ABC123")
    """
    session = load_amazon_session()
    if not session:
        return None

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            storage_state={"cookies": session["cookies"], "origins": session["storage"].get("origins", [])}
        )
        page = context.new_page()

        url = f"https://www.amazon.com/dp/{asin}"
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Try to extract price (selector may vary)
        try:
            price_text = page.locator('[data-a-color="price"]').first.text_content()
            title = page.locator("h1 span").first.text_content()

            result = {
                "asin": asin,
                "title": title,
                "price": price_text,
                "url": url,
                "checked_at": datetime.now().isoformat(),
            }

            browser.close()
            return result

        except Exception as e:
            print(f"Error checking price for {asin}: {e}")
            browser.close()
            return None


def amazon_buy_now(asin: str, quantity: int = 1) -> bool:
    """
    Add item to cart and navigate to checkout using saved session.
    Returns True if successful, False otherwise.
    """
    session = load_amazon_session()
    if not session:
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state={"cookies": session["cookies"], "origins": session["storage"].get("origins", [])}
        )
        page = context.new_page()

        try:
            # Navigate to product
            url = f"https://www.amazon.com/dp/{asin}"
            page.goto(url)
            page.wait_for_load_state("networkidle")

            # Add to cart
            print(f"Adding {asin} to cart...")
            add_to_cart_btn = page.locator('input[aria-label*="Add to Cart"]').first
            add_to_cart_btn.click()
            page.wait_for_timeout(2000)

            # Navigate to cart
            page.goto("https://www.amazon.com/gp/cart/view.html")
            page.wait_for_load_state("networkidle")

            # Go to checkout
            print("Proceeding to checkout...")
            checkout_btn = page.locator('a[href*="gp/checkout"]').first
            if checkout_btn:
                checkout_btn.click()
                page.wait_for_timeout(3000)
                print("✓ Navigated to checkout. Complete payment manually.")
            else:
                print("Checkout button not found")
                return False

            # Keep browser open for manual payment
            print("\n⏳ Browser staying open for you to complete payment.")
            print("   Close the browser window when done.")
            browser.wait_for_event("close")

            return True

        except Exception as e:
            print(f"Error during checkout: {e}")
            return False
        finally:
            if browser:
                browser.close()


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Gmail + Amazon Automation Catchall",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python catchall.py --gmail                          # Download all attachments
  python catchall.py --gmail --query "from:boss@example.com"
  python catchall.py --amazon-price B000ABC123       # Check price by ASIN
  python catchall.py --amazon-buy B000ABC123 --qty 2 # Add to cart + checkout
  python catchall.py --amazon-login                   # One-time login setup
        """,
    )

    parser.add_argument(
        "--gmail",
        action="store_true",
        help="Download Gmail attachments",
    )
    parser.add_argument(
        "--query",
        default="has:attachment",
        help="Gmail search query (default: has:attachment)",
    )
    parser.add_argument(
        "--amazon-price",
        metavar="ASIN",
        help="Check Amazon price (provide ASIN, e.g., B000ABC123)",
    )
    parser.add_argument(
        "--amazon-buy",
        metavar="ASIN",
        help="Add to cart and go to checkout (provide ASIN)",
    )
    parser.add_argument(
        "--qty",
        type=int,
        default=1,
        help="Quantity for purchase (default: 1)",
    )
    parser.add_argument(
        "--amazon-login",
        action="store_true",
        help="One-time Amazon login setup",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("VIRELUNE CATCHALL — Gmail + Amazon Automation")
    print("=" * 70)
    print(f"Config directory: {CONFIG_DIR}\n")

    # Gmail attachment download
    if args.gmail:
        try:
            print(f"📧 Downloading Gmail attachments (query: '{args.query}')...")
            attachments = download_gmail_attachment(query=args.query)
            if attachments:
                print(f"   ✓ Found {len(attachments)} attachment(s)")
                for att in attachments:
                    print(f"     • {att['filename']} from {att['sender']}")
            else:
                print("   ℹ️  No attachments found")
        except FileNotFoundError as e:
            print(f"   ❌ Error: {e}")
            print("   → Complete Gmail OAuth setup in SETUP.md, Step 1")

    # Amazon price check
    elif args.amazon_price:
        try:
            print(f"💰 Checking Amazon price for ASIN: {args.amazon_price}...")
            price_info = amazon_check_price(args.amazon_price)
            if price_info:
                print(f"   ✓ {price_info['title']}")
                print(f"   Price: {price_info['price']}")
                print(f"   URL: {price_info['url']}")
            else:
                print("   ❌ Could not fetch price (session may have expired)")
                print("   → Run: python catchall.py --amazon-login")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Amazon checkout flow
    elif args.amazon_buy:
        try:
            print(f"🛒 Adding {args.amazon_buy} (qty: {args.qty}) to cart...")
            success = amazon_buy_now(args.amazon_buy, quantity=args.qty)
            if success:
                print(f"   ✓ Checkout flow opened. Complete payment manually.")
            else:
                print(f"   ❌ Checkout failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # One-time Amazon login
    elif args.amazon_login:
        try:
            print("🔐 Starting Amazon login...")
            amazon_login_once()
            print("   ✓ Amazon session saved!")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # No args provided - show help
    else:
        parser.print_help()
        print("\n" + "=" * 70)
        print("✓ Catchall loaded! Choose an option above to get started.")
        print("=" * 70)
