import json
import requests
import os
import uuid
import datetime
import difflib
from langchain.tools import Tool


# --- 1. Search Knowledge Base ---
def search_kb(question: str, k: int = 3):
    """Search the local FAQ database for the most relevant entries."""
    try:
        with open("data/faq.json", "r", encoding="utf-8") as f:
            kb = json.load(f)
    except FileNotFoundError:
        return ["Knowledge base not found."]

    # Fuzzy match for flexible search
    questions = [article["q"] for article in kb]
    close_matches = difflib.get_close_matches(question, questions, n=k, cutoff=0.4)

    if not close_matches:
        return ["No direct match found; consider escalating."]

    # Collect responses for close matches
    responses = [
        f"Q: {article['q']} | A: {article['a']}"
        for match in close_matches
        for article in kb if article["q"] == match
    ]
    return responses


# --- 2. Create Support Ticket ---
def create_ticket(issue: str, customer_email: str = "unknown@customer.com"):
    """Create a support ticket and send it to the configured webhook."""
    webhook = os.getenv("TICKETING_WEBHOOK")
    if not webhook:
        return "❌ Error: Missing TICKETING_WEBHOOK in environment variables."

    payload = {
        "id": str(uuid.uuid4()),
        "issue": issue,
        "email": customer_email,
        "timestamp": datetime.datetime.now().isoformat()
    }

    try:
        response = requests.post(webhook, json=payload, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"⚠️ Ticket creation failed: {e}"

    return f"✅ Ticket created successfully (ID: {payload['id']})"


# --- 3. Save Chat Transcript ---
def save_log(content: str):
    """Save the conversation transcript to a timestamped JSON file."""
    os.makedirs("logs", exist_ok=True)
    filename = datetime.datetime.now().strftime("logs/%Y%m%d_%H%M%S.json")

    log_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session": content
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    return f"📁 Transcript saved to {filename}"


# --- Tool Registry ---
tools = [
    Tool(name="search_kb", func=search_kb, description="Search the insurance FAQ knowledge base."),
    Tool(name="create_ticket", func=create_ticket, description="Create a support ticket if the KB answer is insufficient."),
    Tool(name="save_log", func=save_log, description="Save the chat transcript.")
]

# Convenience map for quick tool lookup
tool_map = {tool.name: tool for tool in tools}
