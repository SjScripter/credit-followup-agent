# Credit Follow-Up Email Agent
### AI Enablement Internship — Task 2 | Travel Corporation India (TCI)

---

## Project Overview

The Credit Follow-Up Email Agent is an AI-powered automation tool built for the Finance team at Travel Corporation India. It automatically identifies overdue invoices, determines the correct escalation stage based on the number of days overdue, and generates personalised, professional follow-up emails using a Large Language Model (LLM).

The agent operates in dry-run mode by default, meaning all emails are generated and logged without actually being sent — making it safe to demo and test on real business data.

---

## Business Problem

Finance teams spend significant time manually chasing overdue payments. These follow-ups are often inconsistent in tone and timing. This agent automates the workflow, escalates appropriately, and logs every interaction for audit — reducing Days Sales Outstanding (DSO) while maintaining professional client relationships.

---

## Features

- Automatic ingestion of invoice data from CSV
- Auto-calculation of days overdue from today's date
- Tone escalation across 4 stages based on days overdue
- LLM-generated personalised emails for each debtor
- Legal escalation flag for invoices overdue by 30+ days
- Full audit trail saved to JSON with timestamp, tone, stage, and status
- Streamlit dashboard for visual monitoring and control
- Dry-run mode for safe testing without sending real emails
- Downloadable audit log in JSON format

---

## Tone Escalation Matrix

| Stage | Days Overdue | Tone | Action |
|-------|-------------|------|--------|
| Stage 1 | 1 - 7 days | Warm and Friendly | Gentle reminder |
| Stage 2 | 8 - 14 days | Polite but Firm | Request confirmation |
| Stage 3 | 15 - 21 days | Formal and Serious | Escalating concern |
| Stage 4 | 22 - 30 days | Stern and Urgent | Final reminder |
| Escalation | 30+ days | Legal Flag | Assigned to finance manager |

---

## Agent Flow

```
CSV Invoice Data
      |
      v
Trigger Logic (auto-calculate days overdue from today's date)
      |
      v
Escalation Engine (determine stage based on days overdue)
      |
      v
LLM Email Generator (Groq — Llama 3.3 70B)
      |
      v
Audit Logger (save to logs/email_log.json)
      |
      v
Streamlit Dashboard (visual monitoring + control)
```

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| LLM | Groq — Llama 3.3 70B Versatile | Free tier, fast inference, excellent instruction following |
| Agent Framework | LangChain | Industry standard, easy LLM integration, structured output support |
| Data Source | CSV via pandas | Simple, portable, matches the task requirement |
| Email Send | Dry-run log (JSON) | Safe for testing, meets task requirement |
| UI | Streamlit | Fast to build, clean interface, easy to demo |
| Logging | JSON file | Lightweight, human-readable audit trail |
| Environment | python-dotenv | Secure API key management |

---

## LLM Choice Justification

**Model:** Llama 3.3 70B Versatile via Groq API

- Free tier with generous rate limits — no billing required
- Extremely fast inference (Groq hardware)
- Strong instruction following for structured JSON output
- Reliable for professional email generation across multiple tones
- Groq API is OpenAI-compatible making it easy to swap models if needed

---

## Project Structure

```
credit-followup-agent/
├── app.py                        # Streamlit dashboard
├── main.py                       # Terminal runner
├── requirements.txt              # Python dependencies
├── .env.example                  # Safe environment variable template
├── .gitignore                    # Excludes .env and cache files
├── agent/
│   ├── __init__.py
│   ├── escalation_engine.py      # Stage determination logic
│   ├── email_generator.py        # LLM email generation
│   └── audit_logger.py           # JSON audit trail
├── data/
│   └── invoices.csv              # Mock invoice data
└── logs/
    └── email_log.json            # Auto-generated audit log
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/SjScripter/credit-followup-agent.git
cd credit-followup-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```
Open `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free key at: https://console.groq.com

### 4. Run via terminal
```bash
python main.py
```

### 5. Run Streamlit dashboard
```bash
streamlit run app.py
```

---

## Sample Output

### Terminal
```
============================================================
  CREDIT FOLLOW-UP EMAIL AGENT
  Today: 2026-05-09
  Mode: DRY RUN
============================================================

Loaded 5 invoices

Processing: INV-2024-001 | Rajesh Kapoor | 5 days overdue
  Generating Warm & Friendly email...
  Subject: 1st Follow-Up: Overdue Payment for INV-2024-001
  Preview: Dear Rajesh Kapoor, I hope this email finds you well...
  [LOG] INV-2024-001 → Stage 1 (dry-run)

Processing: INV-2024-004 | Neha Gupta | 35 days overdue
  FLAGGED FOR LEGAL REVIEW — no email sent.
  [LOG] INV-2024-004 → Stage 5 (flagged)

============================================================
  AGENT RUN COMPLETE
  Log saved to: logs/email_log.json
============================================================
```

---

## Security Risk Mitigation

| Risk | Description | Mitigation |
|------|-------------|------------|
| Prompt Injection | Malicious invoice data manipulating LLM behaviour | All invoice fields are passed as structured variables, not raw user input. LLM is instructed to return JSON only. |
| API Key Exposure | Groq API key leaked in source code | API key stored in .env file. .env added to .gitignore. .env.example provided with placeholder values only. |
| Data Privacy / PII | Invoice data contains personal client information | Data processed locally. No PII sent to external services beyond the LLM prompt. Logs stored locally. |
| Hallucination Risk | LLM generating incorrect email content or wrong client details | Structured JSON output enforced via system prompt. All invoice fields injected directly from data source. Human review via dashboard before any live send. |
| Unauthorised Access | Anyone triggering the agent | Agent runs locally. No public endpoint exposed. Dry-run mode enabled by default. |
| Accidental Email Send | Emails sent to real clients during testing | Dry-run mode is ON by default. Live send requires manual toggle in the dashboard. |

---

## Prompt Design

### System Prompt
The LLM is given a strict system prompt instructing it to:
- Act as a professional finance communication assistant
- Always personalise emails with exact client details from the data
- Return only a valid JSON object with subject and body keys
- Never generate generic content

### User Prompt
Each user prompt includes:
- Client name, invoice number, amount, due date, days overdue
- The escalation stage label and tone
- The specific call to action for that stage

### Guardrails Applied
- JSON-only output enforced in system prompt
- Markdown code fence stripping in parser
- Try/catch error handling on JSON parsing
- All client fields injected from structured data source — not from free text input

---

## Mandatory Disclosures

| Item | Detail |
|------|--------|
| LLM Model | Llama 3.3 70B Versatile via Groq API (free tier) |
| Agent Framework | LangChain with LangChain-Groq integration |
| Architecture | Linear pipeline — trigger, escalate, generate, log |
| Prompt Strategy | Structured JSON output with field injection |
| Security | .env for keys, dry-run default, local processing |

---

## Submitted By

**Name:** Sarthak  
**GitHub:** https://github.com/SjScripter  
**Internship:** AI Enablement — Travel Corporation India (TCI)  
**Task:** Task 2 — Finance Credit Follow-Up Email Agent
