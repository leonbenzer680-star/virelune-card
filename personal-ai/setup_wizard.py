#!/usr/bin/env python3
"""
Personal AI Assistant - Automated Setup Wizard
Guides you through everything step-by-step
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from dotenv import load_dotenv


class SetupWizard:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / "config"
        self.env_file = self.project_root / ".env"

    def clear_screen(self):
        """Clear terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60 + "\n")

    def print_step(self, number, text):
        """Print step number"""
        print(f"\n📍 STEP {number}: {text}")
        print("-" * 60)

    def ask_yes_no(self, question):
        """Ask yes/no question"""
        while True:
            response = input(f"\n{question} (yes/no): ").lower().strip()
            if response in ["yes", "y"]:
                return True
            elif response in ["no", "n"]:
                return False
            print("Please answer 'yes' or 'no'")

    def run(self):
        """Run the setup wizard"""
        self.clear_screen()
        self.print_header("PERSONAL AI ASSISTANT - SETUP WIZARD")

        print("This wizard will guide you through setup in 3 simple steps:\n")
        print("1. Add Claude API Key")
        print("2. Get Google OAuth Credentials")
        print("3. Authenticate Everything")
        print("\nTotal time: ~15 minutes\n")

        if not self.ask_yes_no("Ready to start?"):
            print("\nSetup cancelled. Run this script again when ready!")
            return

        # Step 1: Claude API Key
        self.setup_claude_key()

        # Step 2: Google OAuth
        self.setup_google_oauth()

        # Step 3: Test Everything
        self.test_system()

        # Completion
        self.print_header("✅ SETUP COMPLETE!")
        self.show_next_steps()

    def setup_claude_key(self):
        """Step 1: Setup Claude API Key"""
        self.print_step(1, "Claude API Key")

        print("You need a Claude API key from Anthropic.")
        print("\nI'll open the website for you now...\n")

        if self.ask_yes_no("Ready to get your Claude API key?"):
            webbrowser.open("https://console.anthropic.com/account/keys")

            print("\n✓ Browser opened to: https://console.anthropic.com/account/keys")
            print("\nWhat to do:")
            print("  1. Click 'Create Key'")
            print("  2. Copy your API key")
            print("  3. Come back here and paste it\n")

            api_key = input("Paste your Claude API key here: ").strip()

            if not api_key:
                print("❌ No key provided. Setup cancelled.")
                return

            # Update .env file
            self.update_env("CLAUDE_API_KEY", api_key)
            print("\n✅ Claude API key saved to .env")

    def setup_google_oauth(self):
        """Step 2: Setup Google OAuth"""
        self.print_step(2, "Google OAuth Credentials")

        print("You need OAuth credentials from Google Cloud Console.")
        print("This involves 3 sub-steps:\n")
        print("  a) Create a Google Cloud project")
        print("  b) Enable APIs (Gmail, Drive, Docs, Sheets)")
        print("  c) Create OAuth credentials")

        print("\nI'll guide you through each step...\n")

        # Step 2a: Create Project
        if self.ask_yes_no("Ready to create a Google Cloud project?"):
            webbrowser.open("https://console.cloud.google.com")

            print("\n✓ Browser opened to Google Cloud Console")
            print("\nWhat to do:")
            print("  1. Click the project dropdown (top left)")
            print("  2. Click 'NEW PROJECT'")
            print("  3. Name it: 'Personal AI'")
            print("  4. Click 'CREATE'")
            print("  5. Wait for project to be created")
            print("  6. Select the new project from dropdown\n")

            input("Press Enter when done...")

        # Step 2b: Enable APIs
        print("\n\nNow enabling APIs...")
        print("\nWhat to do:")
        print("  1. Click hamburger menu (☰) top left")
        print("  2. Click 'APIs & Services'")
        print("  3. Click 'Enable APIs and Services'")
        print("  4. Search for and enable each API:")
        print("     - Gmail API")
        print("     - Google Drive API")
        print("     - Google Docs API")
        print("     - Google Sheets API")
        print("  5. Come back here when done\n")

        input("Press Enter when APIs are enabled...")

        # Step 2c: Create OAuth Credentials
        print("\n\nCreating OAuth credentials...")
        print("\nWhat to do:")
        print("  1. Click 'Credentials' in left sidebar")
        print("  2. Click 'Create Credentials' → 'OAuth 2.0 Client IDs'")
        print("  3. Select 'Desktop Application'")
        print("  4. Click 'Create'")
        print("  5. Click the DOWNLOAD icon (right side)")
        print("  6. A file 'client_secret_*.json' will download")
        print("  7. Rename it to 'credentials.json'")
        print("  8. Copy it to: personal-ai/config/credentials.json\n")

        credentials_file = self.project_root / "config" / "credentials.json"

        while not credentials_file.exists():
            response = input(
                "Did you save credentials.json to personal-ai/config/? (yes/no): "
            ).lower().strip()
            if response in ["yes", "y"]:
                if credentials_file.exists():
                    print("✅ credentials.json found!")
                    break
                else:
                    print("❌ File not found at personal-ai/config/credentials.json")
                    print("   Please check the path and try again")
            elif response in ["no", "n"]:
                print("When you have the file, copy it and come back")
                return

    def test_system(self):
        """Step 3: Test the system"""
        self.print_step(3, "Start Server and Authenticate")

        print("Now we'll start the server and authenticate services.\n")

        print("What to do:")
        print("  1. Open a NEW terminal window in personal-ai folder")
        print("  2. Run these commands:")
        print("")
        print("     .\\venv\\Scripts\\Activate.ps1")
        print("     python main.py")
        print("")
        print("  3. The server will start on http://localhost:8000")
        print("  4. Leave this server running")
        print("  5. Come back to THIS window and press Enter\n")

        input("Press Enter when server is running...")

        print("\n✓ Great! Now let's authenticate Gmail and Drive...")
        print("\nI can help you authenticate, or you can do it manually.")

        if self.ask_yes_no("Should I try to authenticate automatically?"):
            print("\n(Automatic authentication would open browser)")
            print("For now, Gmail will authenticate when you first use it.")

    def update_env(self, key, value):
        """Update .env file"""
        load_dotenv()

        env_content = ""
        key_found = False

        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                for line in f:
                    if line.startswith(f"{key}="):
                        env_content += f"{key}={value}\n"
                        key_found = True
                    else:
                        env_content += line

        if not key_found:
            env_content += f"{key}={value}\n"

        with open(self.env_file, "w") as f:
            f.write(env_content)

    def show_next_steps(self):
        """Show what's next"""
        print("\n✅ Setup Complete!\n")
        print("Your Personal AI Assistant is ready to use.\n")

        print("📱 To use on iPhone:")
        print("  1. Make sure Tailscale is installed on both laptop and iPhone")
        print("  2. Both signed into SAME Tailscale account")
        print("  3. Create iPhone Shortcut (see QUICK_START.txt)")
        print("  4. Use: 'Hey Siri, Ask my AI [question]'\n")

        print("💻 To use on laptop:")
        print("  1. Make sure server is running: python main.py")
        print("  2. Open: http://localhost:8000")
        print("  3. You'll see the dashboard\n")

        print("📚 Next steps:")
        print("  1. Read ACTIVATE_ABC.md for details")
        print("  2. Add more services (Calendar, Contacts, etc.)")
        print("  3. Enjoy your personal AI!\n")

        print("Questions? Check the documentation files:")
        print("  - QUICK_START.txt")
        print("  - ACTIVATE_ABC.md")
        print("  - COMPLETE_SETUP.md\n")

        input("Press Enter to finish setup...")
        self.clear_screen()
        print("✅ All done! Start using your AI assistant! 🚀\n")


if __name__ == "__main__":
    try:
        wizard = SetupWizard()
        wizard.run()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
