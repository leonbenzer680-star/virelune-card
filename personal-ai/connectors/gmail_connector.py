"""Gmail Connector - Read and manage emails"""

import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.oauthlib.flow import Flow
from googleapiclient.discovery import build
from pathlib import Path

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailConnector:
    """Connect to Gmail API and manage emails"""

    def __init__(self, credentials_file="config/credentials.json"):
        """Initialize Gmail connector with OAuth"""
        self.credentials_file = Path(__file__).parent.parent / credentials_file
        self.token_file = Path(__file__).parent.parent / "config" / "gmail_token.json"
        self.service = None
        self.authenticated = False

    def authenticate(self):
        """Authenticate with Gmail API"""
        try:
            # Check if token exists
            if self.token_file.exists():
                logger.info("Using existing Gmail token")
                from google.auth.transport.requests import Request
                from google.oauth2.credentials import Credentials

                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
                if creds.valid:
                    self.service = build("gmail", "v1", credentials=creds)
                    self.authenticated = True
                    logger.info("Gmail authenticated from token")
                    return True

            # Create new authorization flow
            if not self.credentials_file.exists():
                logger.error(f"Credentials file not found: {self.credentials_file}")
                logger.error("Go to Google Cloud Console to create credentials.json")
                return False

            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file), SCOPES
            )
            creds = flow.run_local_server(port=0)

            # Save token for next time
            with open(self.token_file, "w") as token_file:
                token_file.write(creds.to_json())

            self.service = build("gmail", "v1", credentials=creds)
            self.authenticated = True
            logger.info("Gmail authenticated with new token")
            return True

        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            return False

    def get_recent_emails(self, max_results=5):
        """Get recent emails"""
        if not self.authenticated:
            return []

        try:
            results = self.service.users().messages().list(
                userId="me", maxResults=max_results
            ).execute()

            messages = results.get("messages", [])
            emails = []

            for message in messages:
                msg = self.service.users().messages().get(
                    userId="me", id=message["id"]
                ).execute()
                emails.append(self._parse_message(msg))

            logger.info(f"Retrieved {len(emails)} recent emails")
            return emails

        except Exception as e:
            logger.error(f"Error getting emails: {e}")
            return []

    def search_emails(self, query, max_results=5):
        """Search emails by query"""
        if not self.authenticated:
            return []

        try:
            results = self.service.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()

            messages = results.get("messages", [])
            emails = []

            for message in messages:
                msg = self.service.users().messages().get(
                    userId="me", id=message["id"]
                ).execute()
                emails.append(self._parse_message(msg))

            logger.info(f"Search '{query}' returned {len(emails)} emails")
            return emails

        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []

    def _parse_message(self, message):
        """Parse Gmail message"""
        try:
            headers = message["payload"]["headers"]
            body = ""

            if "parts" in message["payload"]:
                part = message["payload"]["parts"][0]
                if "data" in part["body"]:
                    import base64
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
            else:
                if "data" in message["payload"]["body"]:
                    import base64
                    body = base64.urlsafe_b64decode(
                        message["payload"]["body"]["data"]
                    ).decode("utf-8")

            return {
                "id": message["id"],
                "from": next((h["value"] for h in headers if h["name"] == "From"), "Unknown"),
                "subject": next((h["value"] for h in headers if h["name"] == "Subject"), "No subject"),
                "date": next((h["value"] for h in headers if h["name"] == "Date"), ""),
                "preview": body[:200] if body else "No preview",
                "full_body": body
            }
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return {
                "id": message.get("id"),
                "from": "Unknown",
                "subject": "Error parsing",
                "preview": "Could not parse email"
            }

    def get_unread_count(self):
        """Get count of unread emails"""
        if not self.authenticated:
            return 0

        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            unread_label = next(
                (label for label in labels if label["name"] == "UNREAD"),
                None
            )

            if unread_label:
                return unread_label.get("messagesUnread", 0)
            return 0

        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0

    def check_health(self):
        """Check if Gmail connection is working"""
        try:
            self.service.users().getProfile(userId="me").execute()
            logger.info("Gmail health check: OK")
            return True
        except Exception as e:
            logger.error(f"Gmail health check failed: {e}")
            return False
