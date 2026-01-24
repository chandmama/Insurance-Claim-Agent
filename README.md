# Insurance-Claim-Agent
# Insurance Claim Support Assistant 🤖

A smart, AI-powered insurance claim assistant built using *LangChain, **Google Gemini (Gemini 2.5 Flash), and **Streamlit*.

The assistant can answer insurance FAQs, escalate unresolved issues via tickets, and automatically log chat sessions while maintaining professionalism and empathy.

---

## Overview

### Goals

- Automate customer support for insurance queries

- Retrieve information from a FAQ knowledge base

- Escalate complex or unresolved queries via ticket creation

- Maintain chat logs for each session

- Provide a Streamlit web interface for users

### Key Features

- AI-driven FAQ query answering

- Automatic ticket escalation via webhook

- Session transcript logging

- Streamlit-based web interface

- Robust structured JSON parsing with LangChain OutputFixingParser

---

## Tech Stack
- *Python 3.10+*

- *LangChain*: Agent framework for managing tool-based reasoning

- *LangChain-Google-GenAI*: Integrates Gemini 2.5 Flash model

- *Streamlit*: Frontend UI for chat interactions

- *Pydantic*: Data validation and structured output schema

- *python-dotenv*: Environment variable management

- *Requests*: Webhook and API calls for ticket creation

---

## Architecture

### Project Structure

main.py # CLI chat assistant implementation

app.py # Streamlit-based frontend

tools.py # Tool definitions: search\_kb, create\_ticket, save\_log

schema.py # Defines SupportOutput schema for structured responses

data/faq.json # Local knowledge base for insurance FAQs

logs/ # Auto-generated session logs

.env # Environment variables (API key, webhook URL)

README.md # Project documentation

---

### Flow

1. *User asks a query* → Agent searches search_kb in the knowledge base.

2. *No FAQ match* → Agent escalates via create_ticket.

3. *Response generated* → Output parsed and validated through \OutputFixingParser\.

4. *Session complete* → Transcript logged via save_log.

---

## Setup

### Instructions

1. Clone the repository:

```bash

git clone https://github.com//insurance-support-assistant.git

Navigate to the project folder:

bash


cd insurance-support-assistant

Create a virtual environment:

bash

python -m venv venv

source venv/bin/activate # macOS/Linux

venv\\Scripts\\activate # Windows

Install dependencies:

bash

pip install -r requirements.txt

Configure environment variables in .env:

ini

GOOGLE_API_KEY=your_google_api_key_here

TICKETING_WEBHOOK=https://your-webhook-url.com/tickets

Execution

CLI Mode

Run the assistant in command-line mode:

bash

python main.py

Example interaction:

vbnet


🤖 Insurance Claim Support Assistant

Customer: How long does it take to process a claim?

Agent: Please allow up to 10 business days for final approval.

Web Mode

Run the assistant as a Streamlit web application:

bash

streamlit run app.py

Visit: http://localhost:8501

Features:

Type questions and receive structured responses

Auto-saves chat logs to /logs

Reload previous sessions via sidebar

Handles structured JSON outputs seamlessly

System Prompt:

You are a professional, empathetic, and knowledgeable Insurance Support Assistant.

Core Responsibilities:

1. Retrieve Information: Use search_kb first.

2. Escalate When Needed: Use create_ticket if information is unclear.

3. Maintain Records: Use save_log after every interaction.

4. Tone & Style: Be courteous, concise, and empathetic.

Response Format:

Respond ONLY in JSON structure defined by SupportOutput.

Important:

- Do NOT include markdown or commentary outside JSON.

- If unsure, return empty string/list.

Tools

NameDescriptionLocation

search_kbSearch the insurance FAQ knowledge basetools.py

create_ticketEscalate unresolved issues via webhooktools.py

save_logSave full chat transcript to logs directorytools.py

Schema: SupportOutput

answer: Main response string returned to user

sources: List of knowledge base references

action_taken: Description of any tool-based action performed

Used by OutputFixingParser to enforce valid JSON structure.

Examples

Answered from KB

How long does it usually take to process a claim?

Can I update my beneficiary online?

What happens if I miss a premium payment?

Escalated Tickets

My claim has been under review for weeks with no update.

I lost my insurance documents — can someone help?

I can’t log in to my portal even after resetting the password.

Sample FAQ

QuestionAnswer

Is my claim under review?There is a delay due to high claim volumes. We appreciate your patience.

How long does it usually take to process a claim?Please allow up to 10 business days for final approval.

How can I check my policy coverage?You can view your policy coverage details online or in your policy PDF.

Logs

Stored in JSON format under /logs

Sample:

json

{

"timestamp": "2025-10-25T14:30:21",

"messages": \[

{"role": "user", "content": "Can I cancel my insurance policy?"},

{"role": "assistant", "content": "You can cancel your policy through our app or by calling customer service."}

\]

}

Troubleshooting

Invalid JSON output: Handled automatically using OutputFixingParser.

Missing TICKETING\_WEBHOOK: Ensure it is defined in .env.

No faq.json found: Add or verify data/faq.json exists.

Streamlit not launching: Run streamlit run app.py in the correct project directory.

Contributing

Pull requests and contributions are welcome.

Please ensure proper formatting and testing before submitting PRs. Open issues for bug reports or enhancement suggestions.
