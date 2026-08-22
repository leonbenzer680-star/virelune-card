#!/usr/bin/env python3
"""Personal AI Assistant - Main Server"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/activity.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import connectors
sys.path.insert(0, str(Path(__file__).parent))
from connectors.claude_connector import ClaudeConnector
from connectors.gmail_connector import GmailConnector
from connectors.drive_connector import DriveConnector

# Initialize FastAPI
app = FastAPI(
    title="Personal AI Assistant",
    description="Free-first personal AI system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
config_path = Path(__file__).parent / "config" / "settings.json"
with open(config_path) as f:
    CONFIG = json.load(f)

# Initialize Claude connector
try:
    claude = ClaudeConnector()
    CLAUDE_ENABLED = True
    logger.info("Claude connector initialized")
except Exception as e:
    logger.warning(f"Claude not available: {e}")
    claude = None
    CLAUDE_ENABLED = False

# Initialize Gmail connector
gmail = GmailConnector()
GMAIL_ENABLED = False

# Initialize Drive connector
drive = DriveConnector()
DRIVE_ENABLED = False

logger.info("Starting Personal AI Assistant")

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve dashboard"""
    return get_dashboard_html()

@app.get("/api/status")
async def status():
    """Get system status"""
    claude_health = False
    if claude:
        claude_health = claude.check_health()

    return {
        "status": "running",
        "app": CONFIG["app"],
        "services": {
            "gmail": CONFIG["services"]["gmail"]["enabled"],
            "calendar": CONFIG["services"]["calendar"]["enabled"],
            "contacts": CONFIG["services"]["contacts"]["enabled"],
            "drive": CONFIG["services"]["drive"]["enabled"],
            "sheets": CONFIG["services"]["sheets"]["enabled"],
            "docs": CONFIG["services"]["docs"]["enabled"],
        },
        "claude": {
            "enabled": CLAUDE_ENABLED,
            "healthy": claude_health,
            "model": "claude-3-5-sonnet-20241022" if CLAUDE_ENABLED else None
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ask")
async def ask(request: Request):
    """Handle AI requests from iPhone Shortcut or API"""
    try:
        body = await request.json()
        question = body.get("question", "")

        if not question:
            raise HTTPException(status_code=400, detail="No question provided")

        logger.info(f"Received question: {question}")

        # Check if Claude is available
        if not CLAUDE_ENABLED or not claude:
            logger.warning("Claude not available, returning placeholder response")
            return {
                "status": "warning",
                "question": question,
                "answer": "Claude API not configured. Add CLAUDE_API_KEY to .env file.",
                "timestamp": datetime.now().isoformat()
            }

        # Get response from Claude
        context = {
            "services": [
                service for service, config in CONFIG["services"].items()
                if config.get("enabled", False)
            ]
        }

        claude_response = claude.ask(question, context=context)

        response = {
            "status": claude_response.get("status", "success"),
            "question": question,
            "answer": claude_response.get("answer", "No response"),
            "model": claude_response.get("model", "claude-3-5-sonnet"),
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Response sent to user")
        return response

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    return CONFIG


@app.post("/api/gmail/auth")
async def gmail_authenticate():
    """Authenticate with Gmail"""
    try:
        if gmail.authenticate():
            global GMAIL_ENABLED
            GMAIL_ENABLED = True
            logger.info("Gmail authenticated")
            return {"status": "success", "message": "Gmail authenticated"}
        else:
            return {"status": "error", "message": "Gmail authentication failed"}
    except Exception as e:
        logger.error(f"Gmail auth error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/gmail/recent")
async def get_recent_emails():
    """Get recent emails"""
    if not GMAIL_ENABLED:
        return {"status": "error", "message": "Gmail not authenticated"}

    try:
        emails = gmail.get_recent_emails(max_results=5)
        return {
            "status": "success",
            "emails": emails,
            "count": len(emails),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting emails: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/gmail/search")
async def search_emails(q: str = ""):
    """Search emails"""
    if not GMAIL_ENABLED:
        return {"status": "error", "message": "Gmail not authenticated"}

    if not q:
        return {"status": "error", "message": "Search query required"}

    try:
        emails = gmail.search_emails(q, max_results=5)
        return {
            "status": "success",
            "query": q,
            "emails": emails,
            "count": len(emails),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching emails: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/drive/auth")
async def drive_authenticate():
    """Authenticate with Drive"""
    try:
        if GMAIL_ENABLED:
            # Share Gmail authentication with Drive
            drive.set_service(gmail.service)
            global DRIVE_ENABLED
            DRIVE_ENABLED = True
            logger.info("Drive authenticated")
            return {"status": "success", "message": "Drive authenticated"}
        else:
            return {"status": "error", "message": "Gmail must be authenticated first"}
    except Exception as e:
        logger.error(f"Drive auth error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/drive/search")
async def search_drive(q: str = ""):
    """Search Google Drive"""
    if not DRIVE_ENABLED:
        return {"status": "error", "message": "Drive not authenticated"}

    if not q:
        return {"status": "error", "message": "Search query required"}

    try:
        files = drive.search_files(q, max_results=10)
        return {
            "status": "success",
            "query": q,
            "files": files,
            "count": len(files),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching Drive: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/drive/recent")
async def get_recent_files():
    """Get recent files"""
    if not DRIVE_ENABLED:
        return {"status": "error", "message": "Drive not authenticated"}

    try:
        files = drive.get_recent_files(max_results=10)
        return {
            "status": "success",
            "files": files,
            "count": len(files),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting files: {e}")
        return {"status": "error", "message": str(e)}

# ============================================================================
# DASHBOARD HTML
# ============================================================================

def get_dashboard_html():
    """Generate dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Personal AI Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                color: #333;
            }

            .container {
                max-width: 1000px;
                margin: 0 auto;
            }

            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }

            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }

            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }

            .dashboard {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }

            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
            }

            .card h2 {
                font-size: 1.3em;
                margin-bottom: 15px;
                color: #667eea;
            }

            .status {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 1.1em;
                margin-bottom: 10px;
            }

            .status-badge {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #10b981;
            }

            .status-badge.inactive {
                background: #d1d5db;
            }

            .service-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }

            .service-item {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px;
                background: #f9fafb;
                border-radius: 8px;
                font-size: 0.9em;
            }

            .service-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #10b981;
            }

            .service-dot.inactive {
                background: #d1d5db;
            }

            .button {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                cursor: pointer;
                transition: background 0.3s;
                margin-top: 15px;
                width: 100%;
                text-align: center;
                text-decoration: none;
            }

            .button:hover {
                background: #5568d3;
            }

            .button.secondary {
                background: #e5e7eb;
                color: #333;
            }

            .button.secondary:hover {
                background: #d1d5db;
            }

            .status-text {
                font-size: 0.9em;
                color: #666;
                margin-top: 10px;
            }

            .cost-badge {
                display: inline-block;
                background: #f0fdf4;
                color: #10b981;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8em;
                font-weight: 600;
            }

            .footer {
                text-align: center;
                color: white;
                font-size: 0.9em;
                opacity: 0.8;
            }

            .loading {
                opacity: 0.6;
                pointer-events: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Personal AI Assistant</h1>
                <p>Your free-first AI, running locally</p>
            </div>

            <div class="dashboard" id="dashboard">
                <div class="card loading">
                    <h2>Loading...</h2>
                    <p>Fetching system status...</p>
                </div>
            </div>

            <div class="card">
                <h2>📱 Quick Actions</h2>
                <p style="margin-bottom: 15px; color: #666;">Get started in 3 steps:</p>
                <ol style="margin-left: 20px; line-height: 1.8;">
                    <li>Edit <code>.env</code> with your Claude API key</li>
                    <li>Go to Google Cloud Console to enable APIs</li>
                    <li>Connect services below</li>
                </ol>
                <a href="https://console.anthropic.com" class="button" target="_blank">Get Claude API Key</a>
                <a href="https://console.cloud.google.com" class="button secondary" target="_blank">Google Cloud Console</a>
            </div>

            <div class="footer" style="margin-top: 40px;">
                <p>Personal AI Assistant v0.1.0 • Open source • Privacy first • Zero cost</p>
            </div>
        </div>

        <script>
            async function loadDashboard() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();

                    const html = `
                        <div class="card">
                            <h2>✓ System Status</h2>
                            <div class="status">
                                <span class="status-badge"></span>
                                <span>Server Running</span>
                            </div>
                            <div class="status-text">
                                Version: ${data.app.version}<br>
                                Memory: Local<br>
                                Cost Today: $0.00
                            </div>
                        </div>

                        <div class="card">
                            <h2>📧 Connected Services</h2>
                            <div class="service-grid">
                                <div class="service-item">
                                    <span class="service-dot ${data.services.gmail ? '' : 'inactive'}"></span>
                                    Gmail
                                </div>
                                <div class="service-item">
                                    <span class="service-dot ${data.services.calendar ? '' : 'inactive'}"></span>
                                    Calendar
                                </div>
                                <div class="service-item">
                                    <span class="service-dot ${data.services.contacts ? '' : 'inactive'}"></span>
                                    Contacts
                                </div>
                                <div class="service-item">
                                    <span class="service-dot ${data.services.drive ? '' : 'inactive'}"></span>
                                    Drive
                                </div>
                            </div>
                            <button class="button secondary" onclick="setupServices()">Connect Services</button>
                        </div>

                        <div class="card">
                            <h2>🧠 AI Provider</h2>
                            <div class="status">
                                <span class="status-badge ${data.services.claude ? '' : 'inactive'}"></span>
                                <span>Claude API ${data.services.claude ? '✓ Ready' : '○ Setup Needed'}</span>
                            </div>
                            <div class="status-text">
                                Model: GPT-4 level reasoning<br>
                                Cost: ~$0.50-$5/month<br>
                                <span class="cost-badge">Free-tier compatible</span>
                            </div>
                        </div>

                        <div class="card">
                            <h2>📱 iPhone Setup</h2>
                            <div class="status-text">
                                Status: Ready for Shortcuts<br>
                                Access: Local WiFi or VPN<br>
                                Voice: iPhone native Siri
                            </div>
                            <button class="button secondary" onclick="copyShortcutURL()">Copy Shortcut URL</button>
                        </div>
                    `;

                    document.getElementById('dashboard').innerHTML = html;
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                    document.getElementById('dashboard').innerHTML = `
                        <div class="card" style="grid-column: 1 / -1;">
                            <h2>⚠️ Connection Error</h2>
                            <p>Could not load system status. Make sure the server is running.</p>
                        </div>
                    `;
                }
            }

            function setupServices() {
                alert('Service setup coming soon!\\n\\nFor now: Go to console.cloud.google.com to enable APIs');
            }

            function copyShortcutURL() {
                const ip = window.location.hostname;
                const port = window.location.port || '8000';
                const url = `http://${ip}:${port}/api/ask`;
                navigator.clipboard.writeText(url).then(() => {
                    alert('Shortcut URL copied!\\n\\n' + url);
                });
            }

            // Load dashboard when page loads
            loadDashboard();

            // Refresh every 10 seconds
            setInterval(loadDashboard, 10000);
        </script>
    </body>
    </html>
    """

# ============================================================================
# STARTUP
# ============================================================================

def check_requirements():
    """Check if all requirements are met"""
    if not os.getenv("CLAUDE_API_KEY"):
        logger.warning("⚠️  CLAUDE_API_KEY not set in .env")
        logger.warning("Get your key from: https://console.anthropic.com")

    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)

if __name__ == "__main__":
    check_requirements()

    port = int(os.getenv("SERVER_PORT", 8000))
    host = os.getenv("SERVER_HOST", "0.0.0.0")

    print("\n" + "="*60)
    print("  Personal AI Assistant - Ready to Run")
    print("="*60)
    print(f"\n✓ Server starting at http://localhost:{port}")
    print(f"✓ Dashboard: http://localhost:{port}")
    print(f"✓ API: http://localhost:{port}/api/ask")
    print("\nPress CTRL+C to stop\n")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
