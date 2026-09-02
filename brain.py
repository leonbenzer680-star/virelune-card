import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import zoneinfo
import glob

import requests
from anthropic import Anthropic
from dotenv import load_dotenv
from icalendar import Calendar
from recurring_ical_events import of as recurring_of
from pypdf import PdfReader
import chromadb

load_dotenv()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
LOCAL_TZ = zoneinfo.ZoneInfo(os.getenv("LOCAL_TZ", "America/Los_Angeles"))

VAULT_ROOT = os.getenv("VAULT_ROOT", "./vault")
NOTION_EXPORT_DIR = os.getenv("NOTION_EXPORT_DIR", "./vault/notion")
YOUTUBE_LOG = os.getenv("YOUTUBE_LOG", "./vault/logs/youtube.csv")
BOOK_LOG = os.getenv("BOOK_LOG", "./vault/logs/books.csv")
SEARCH_LOG = os.getenv("SEARCH_LOG", "./vault/logs/searches.csv")
TASK_LOG = os.getenv("TASK_LOG", "./vault/logs/tasks.csv")

# ---------- WEATHER ----------
def fetch_weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = os.getenv("OPENWEATHER_CITY", "Las Vegas")
    country = os.getenv("OPENWEATHER_COUNTRY", "US")
    if not api_key:
        return "Weather: (no API key configured)"
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city},{country}&units=imperial&appid={api_key}"
    )
    r = requests.get(url, timeout=10)
    data = r.json()
    if "list" not in data:
        return "Weather: unable to fetch forecast."
    today = datetime.now(LOCAL_TZ).date()
    today_points = [p for p in data["list"]
                    if datetime.fromtimestamp(p["dt"], LOCAL_TZ).date() == today]
    if not today_points:
        return "Weather: no forecast points for today."
    temps = [p["main"]["temp"] for p in today_points]
    desc = today_points[0]["weather"][0]["description"].capitalize()
    return f"Weather today in {city}: {desc}, avg {sum(temps)/len(temps):.0f}°F."

# ---------- CALENDAR ----------
def fetch_calendar_events():
    urls = [
        os.getenv("PRIMARY_CALENDAR_ICAL"),
        os.getenv("SECONDARY_CALENDAR_ICAL"),
    ]
    today = datetime.now(LOCAL_TZ).date()
    events_out = []
    for url in urls:
        if not url:
            continue
        try:
            r = requests.get(url, timeout=10)
            cal = Calendar.from_ical(r.text)
            events = recurring_of(cal).between(
                datetime.combine(today, datetime.min.time()).replace(tzinfo=LOCAL_TZ),
                datetime.combine(today, datetime.max.time()).replace(tzinfo=LOCAL_TZ),
            )
            for ev in events:
                summary = str(ev.get("summary", "No title"))
                start = ev.get("dtstart").dt
                if isinstance(start, datetime):
                    start_local = start.astimezone(LOCAL_TZ)
                else:
                    start_local = datetime.combine(start, datetime.min.time()).replace(tzinfo=LOCAL_TZ)
                events_out.append(
                    {
                        "title": summary,
                        "time": start_local.strftime("%I:%M %p"),
                        "hour": start_local.hour,
                    }
                )
        except Exception as e:
            events_out.append({"title": f"[Error reading calendar: {e}]", "time": "", "hour": 0})
    if not events_out:
        return "No events on your calendars today."
    # Group by morning/afternoon/evening
    buckets = {"Morning": [], "Afternoon": [], "Evening": []}
    for ev in events_out:
        h = ev["hour"]
        if h < 12:
            buckets["Morning"].append(ev)
        elif h < 17:
            buckets["Afternoon"].append(ev)
        else:
            buckets["Evening"].append(ev)
    lines = []
    for label in ["Morning", "Afternoon", "Evening"]:
        if buckets[label]:
            lines.append(f"{label}:")
            for ev in sorted(buckets[label], key=lambda x: x["time"]):
                lines.append(f"  {ev['time']} — {ev['title']}")
    return "Today's calendar:\n" + "\n".join(lines)

# ---------- SECOND BRAIN INDEX ----------
def init_vector_store():
    client = chromadb.Client()
    collection = client.get_or_create_collection("second_brain")
    return collection

def read_text_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def read_pdf_file(path):
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        return ""

def ingest_vault(collection):
    # Any file under VAULT_ROOT becomes part of the brain
    patterns = [
        "**/*.txt",
        "**/*.md",
        "**/*.pdf",
        "**/*.docx",  # docx will be skipped unless you add a parser
    ]
    docs = []
    ids = []
    metas = []
    for pattern in patterns:
        for path in glob.glob(os.path.join(VAULT_ROOT, pattern), recursive=True):
            if path.endswith(".pdf"):
                content = read_pdf_file(path)
            else:
                content = read_text_file(path)
            if not content.strip():
                continue
            doc_id = f"doc::{path}"
            docs.append(content)
            ids.append(doc_id)
            metas.append({"path": path})
    if docs:
        collection.upsert(documents=docs, ids=ids, metadatas=metas)

def ingest_logs(collection):
    for label, path in [
        ("youtube", YOUTUBE_LOG),
        ("books", BOOK_LOG),
        ("searches", SEARCH_LOG),
    ]:
        if not os.path.exists(path):
            continue
        content = read_text_file(path)
        if not content.strip():
            continue
        doc_id = f"log::{label}"
        collection.upsert(
            documents=[content],
            ids=[doc_id],
            metadatas=[{"type": label, "path": path}],
        )

def build_second_brain_index():
    collection = init_vector_store()
    ingest_vault(collection)
    ingest_logs(collection)
    return collection

def brain_query(collection, question, n_results=8):
    results = collection.query(
        query_texts=[question],
        n_results=n_results,
    )
    chunks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        path = meta.get("path", "unknown")
        chunks.append(f"[{path}]\n{doc[:2000]}")
    return "\n\n".join(chunks) if chunks else "(No matching context found.)"

# ---------- TASKS / REVIEWS ----------
def read_tasks():
    if not os.path.exists(TASK_LOG):
        return []
    lines = read_text_file(TASK_LOG).splitlines()
    tasks = []
    # simple CSV: description,status,date
    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        tasks.append({
            "desc": parts[0],
            "status": parts[1].lower(),  # done / pending / in_progress
            "date": parts[2],
        })
    return tasks

def split_tasks_for_period(period="daily"):
    tasks = read_tasks()
    today = datetime.now(LOCAL_TZ).date()
    if period == "daily":
        target_dates = {today.isoformat()}
    else:
        # last 7 days
        target_dates = {
            (today - timedelta(days=i)).isoformat()
            for i in range(7)
        }
    done = [t for t in tasks if t["status"] == "done" and t["date"] in target_dates]
    pending = [t for t in tasks if t["status"] != "done" and t["date"] in target_dates]
    return done, pending

# ---------- PROMPTS ----------
def build_daily_prompt(weather_text, calendar_text, focus_items, brain_context, done_tasks, pending_tasks):
    today_str = datetime.now(LOCAL_TZ).strftime("%A, %B %d, %Y")
    focus_str = "\n".join(f"- {item}" for item in focus_items)
    done_str = "\n".join(f"- {t['desc']}" for t in done_tasks) or "None logged."
    pending_str = "\n".join(f"- {t['desc']}" for t in pending_tasks) or "None logged."

    return f"""
You are my daily operations assistant and second brain.

Today is {today_str} in Las Vegas (Pacific time).

Weather:
{weather_text}

Calendar:
{calendar_text}

Daily focus:
{focus_str}

Tasks done today:
{done_str}

Tasks still open:
{pending_str}

Second brain context (contracts, agreements, insurance, notes, PDFs, bills, payments, Notion exports, logs):
{brain_context}

I run:
- Specialty Services LLC (service/automation consulting)
- LB Automations (digital product/automation business)

Generate a concise HTML DAILY dashboard email with:
- Calm, practical chief-of-staff tone
- Sections:
  - Today at a glance (weather + key events)
  - Priority list for today (3–7 bullets)
  - Tasks: what got done, what's left
  - Second brain highlights: any critical items or deadlines from the context
  - Systems check: inbox, automations, payments, client messages
- Tight and skimmable. No fluff, no quotes.
Return ONLY HTML, no explanations.
"""

def build_weekly_prompt(brain_context, done_tasks, pending_tasks):
    today_str = datetime.now(LOCAL_TZ).strftime("%A, %B %d, %Y")
    done_str = "\n".join(f"- {t['desc']} ({t['date']})" for t in done_tasks) or "None logged."
    pending_str = "\n".join(f"- {t['desc']} ({t['date']})" for t in pending_tasks) or "None logged."

    return f"""
You are my weekly review agent and second brain.

Today is {today_str} in Las Vegas (Pacific time).

Weekly tasks done:
{done_str}

Weekly tasks still open:
{pending_str}

Second brain context (contracts, agreements, insurance, notes, PDFs, bills, payments, Notion exports, logs):
{brain_context}

Generate a concise HTML WEEKLY review email with:
- Sections:
  - Wins this week (group and summarize done tasks)
  - Open loops (pending tasks + any obvious follow-ups from context)
  - Risk / attention: contracts, payments, renewals, deadlines
  - Suggested focus for next week (3–7 bullets)
- Tight, skimmable, no fluff.
Return ONLY HTML, no explanations.
"""

def generate_html_from_prompt(prompt):
    resp = anthropic.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1600,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text

# ---------- EMAIL ----------
def send_email(html_body, subject):
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    to_addr = os.getenv("SMTP_TO", user)

    if not user or not password:
        print("SMTP not configured; skipping email send.")
        print(html_body)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr

    part_html = MIMEText(html_body, "html")
    msg.attach(part_html)

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())

# ---------- FOCUS ----------
def fetch_daily_focus():
    # Edit this list as your default daily focus.
    return [
        "Top 3 priorities for Specialty Services LLC",
        "Check automation queues for LB Automations",
        "Review any new client leads or support tickets",
    ]

# ---------- ENTRYPOINTS ----------
def run_daily_dashboard():
    collection = build_second_brain_index()
    brain_context = brain_query(collection, "What should I know for today across contracts, payments, and active work?")
    weather = fetch_weather()
    calendar = fetch_calendar_events()
    focus = fetch_daily_focus()
    done, pending = split_tasks_for_period("daily")
    prompt = build_daily_prompt(weather, calendar, focus, brain_context, done, pending)
    html = generate_html_from_prompt(prompt)
    send_email(html, subject="Daily Ops + Second Brain Dashboard")

def run_weekly_review():
    collection = build_second_brain_index()
    brain_context = brain_query(collection, "What matters for my weekly review across all areas of life and business?")
    done, pending = split_tasks_for_period("weekly")
    prompt = build_weekly_prompt(brain_context, done, pending)
    html = generate_html_from_prompt(prompt)
    send_email(html, subject="Weekly Review + Second Brain Summary")

if __name__ == "__main__":
    mode = os.getenv("MODE", "daily")
    if mode == "weekly":
        run_weekly_review()
    else:
        run_daily_dashboard()
