"""Google Drive Connector - Search and read files"""

import os
import logging
from pathlib import Path
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class DriveConnector:
    """Connect to Google Drive API"""

    def __init__(self):
        """Initialize Drive connector"""
        self.service = None
        self.authenticated = False

    def set_service(self, service):
        """Set service from existing authentication"""
        self.service = service
        self.authenticated = True
        logger.info("Drive connector initialized with service")

    def search_files(self, query, max_results=10):
        """Search for files by name or content"""
        if not self.authenticated or not self.service:
            return []

        try:
            # Build search query
            search_query = f"name contains '{query}' and trashed=false"

            results = self.service.files().list(
                q=search_query,
                spaces="drive",
                fields="files(id, name, mimeType, modifiedTime, webViewLink, size)",
                pageSize=max_results
            ).execute()

            files = results.get("files", [])
            logger.info(f"Search '{query}' returned {len(files)} files")

            return [
                {
                    "id": file["id"],
                    "name": file["name"],
                    "type": file["mimeType"],
                    "modified": file.get("modifiedTime", ""),
                    "url": file.get("webViewLink", ""),
                    "size": file.get("size", 0)
                }
                for file in files
            ]

        except Exception as e:
            logger.error(f"Error searching Drive: {e}")
            return []

    def read_document(self, file_id):
        """Read a Google Docs document"""
        if not self.authenticated or not self.service:
            return None

        try:
            # Get document metadata and content
            doc = self.service.documents().get(documentId=file_id).execute()

            # Extract text
            content = ""
            for element in doc.get("body", {}).get("content", []):
                if "paragraph" in element:
                    for run in element["paragraph"].get("elements", []):
                        if "textRun" in run:
                            content += run["textRun"]["content"]

            logger.info(f"Read document: {doc.get('title', 'Unknown')}")

            return {
                "id": file_id,
                "title": doc.get("title", "Unknown"),
                "content": content,
                "length": len(content)
            }

        except Exception as e:
            logger.error(f"Error reading document: {e}")
            return None

    def read_spreadsheet(self, file_id, range_name="Sheet1!A1:Z100"):
        """Read a Google Sheets spreadsheet"""
        if not self.authenticated or not self.service:
            return None

        try:
            sheets = build("sheets", "v4", credentials=self.service._http)
            result = sheets.spreadsheets().values().get(
                spreadsheetId=file_id, range=range_name
            ).execute()

            values = result.get("values", [])
            logger.info(f"Read spreadsheet: {len(values)} rows")

            return {
                "id": file_id,
                "rows": len(values),
                "columns": len(values[0]) if values else 0,
                "data": values
            }

        except Exception as e:
            logger.error(f"Error reading spreadsheet: {e}")
            return None

    def get_recent_files(self, max_results=10):
        """Get recently modified files"""
        if not self.authenticated or not self.service:
            return []

        try:
            results = self.service.files().list(
                spaces="drive",
                fields="files(id, name, mimeType, modifiedTime, webViewLink)",
                pageSize=max_results,
                orderBy="modifiedTime desc",
                q="trashed=false"
            ).execute()

            files = results.get("files", [])
            logger.info(f"Retrieved {len(files)} recent files")

            return [
                {
                    "id": file["id"],
                    "name": file["name"],
                    "type": file["mimeType"],
                    "modified": file.get("modifiedTime", ""),
                    "url": file.get("webViewLink", "")
                }
                for file in files
            ]

        except Exception as e:
            logger.error(f"Error getting recent files: {e}")
            return []

    def check_health(self):
        """Check if Drive connection is working"""
        try:
            self.service.files().list(pageSize=1).execute()
            logger.info("Drive health check: OK")
            return True
        except Exception as e:
            logger.error(f"Drive health check failed: {e}")
            return False
