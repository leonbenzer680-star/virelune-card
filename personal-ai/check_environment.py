#!/usr/bin/env python3
"""
Environment Check Script for Personal AI Assistant
Detects installed software and determines system readiness.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class EnvironmentChecker:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "python": None,
            "pip": None,
            "git": None,
            "node": None,
            "chrome": None,
            "firefox": None,
            "edge": None,
            "platform": sys.platform,
            "notes": []
        }

    def check_python(self):
        try:
            version = sys.version
            self.results["python"] = {
                "installed": True,
                "version": version,
                "executable": sys.executable
            }
            return True
        except:
            self.results["python"] = {"installed": False}
            return False

    def check_command(self, command, version_flag="--version"):
        try:
            result = subprocess.run(
                [command, version_flag],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return {
                    "installed": True,
                    "output": result.stdout.strip() + result.stderr.strip()
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return {"installed": False}

    def check_pip(self):
        self.results["pip"] = self.check_command("pip", "--version")

    def check_git(self):
        self.results["git"] = self.check_command("git", "--version")

    def check_node(self):
        self.results["node"] = self.check_command("node", "--version")

    def check_browsers(self):
        # Chrome locations by platform
        chrome_paths = {
            "win32": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            "darwin": [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ],
            "linux": [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium",
                "/snap/bin/chromium",
            ]
        }

        firefox_paths = {
            "win32": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
            "darwin": [
                "/Applications/Firefox.app/Contents/MacOS/firefox",
            ],
            "linux": [
                "/usr/bin/firefox",
                "/snap/bin/firefox",
            ]
        }

        edge_paths = {
            "win32": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "darwin": [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            ],
            "linux": [
                "/usr/bin/microsoft-edge-stable",
            ]
        }

        for browser_name, paths in [("chrome", chrome_paths), ("firefox", firefox_paths), ("edge", edge_paths)]:
            browser_list = paths.get(sys.platform, [])
            found = False
            for path in browser_list:
                if Path(path).exists():
                    self.results[browser_name] = {
                        "installed": True,
                        "path": path
                    }
                    found = True
                    break
            if not found:
                self.results[browser_name] = {"installed": False}

    def analyze(self):
        """Provide analysis and recommendations."""
        analysis = {
            "ready": True,
            "recommendations": [],
            "blocking_issues": []
        }

        # Check critical requirements
        if not self.results["python"]["installed"]:
            analysis["blocking_issues"].append("Python 3 is required but not found")
            analysis["ready"] = False

        if not self.results["git"]["installed"]:
            analysis["recommendations"].append("Install Git for version control")

        if not self.results["pip"]["installed"]:
            analysis["blocking_issues"].append("pip (Python package manager) required")
            analysis["ready"] = False

        # Check for browser automation capability
        if not any([
            self.results["chrome"]["installed"],
            self.results["firefox"]["installed"],
            self.results["edge"]["installed"]
        ]):
            analysis["recommendations"].append(
                "Install a browser (Chrome, Firefox, or Edge) for web automation"
            )

        return analysis

    def run(self):
        """Run all checks."""
        print("🔍 Checking Environment for Personal AI Assistant...\n")

        self.check_python()
        self.check_pip()
        self.check_git()
        self.check_node()
        self.check_browsers()

        analysis = self.analyze()

        # Display results
        print("📋 INSTALLED SOFTWARE")
        print("=" * 50)
        print(f"Platform: {self.results['platform']}")
        print(f"Python: {'✓' if self.results['python']['installed'] else '✗'}", end="")
        if self.results['python']['installed']:
            print(f" ({self.results['python']['version'].split()[0]})")
        else:
            print()

        print(f"pip: {'✓' if self.results['pip']['installed'] else '✗'}")
        print(f"Git: {'✓' if self.results['git']['installed'] else '✗'}")
        print(f"Node.js: {'✓' if self.results['node']['installed'] else '✗'}")
        print()

        print("🌐 BROWSERS")
        print("=" * 50)
        print(f"Chrome: {'✓' if self.results['chrome']['installed'] else '✗'}")
        print(f"Firefox: {'✓' if self.results['firefox']['installed'] else '✗'}")
        print(f"Edge: {'✓' if self.results['edge']['installed'] else '✗'}")
        print()

        # Display analysis
        if analysis["blocking_issues"]:
            print("⛔ BLOCKING ISSUES")
            print("=" * 50)
            for issue in analysis["blocking_issues"]:
                print(f"  • {issue}")
            print()

        if analysis["recommendations"]:
            print("💡 RECOMMENDATIONS")
            print("=" * 50)
            for rec in analysis["recommendations"]:
                print(f"  • {rec}")
            print()

        print("📊 READINESS")
        print("=" * 50)
        if analysis["ready"]:
            print("✓ System is ready for setup!")
        else:
            print("✗ Please install blocking issues before proceeding")
        print()

        # Save results
        results_file = Path(__file__).parent / "environment_check.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📁 Full results saved to: environment_check.json")

        return analysis["ready"]


if __name__ == "__main__":
    checker = EnvironmentChecker()
    ready = checker.run()
    sys.exit(0 if ready else 1)
