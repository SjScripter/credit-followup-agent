import json
import os
from datetime import datetime

LOG_FILE = "logs/email_log.json"

def load_log() -> list:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_log(log: list):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def log_email(invoice: dict, stage_info: dict, email: dict, status: str = "dry-run"):
    log = load_log()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "invoice_no": invoice["invoice_no"],
        "client_name": invoice["client_name"],
        "client_email": invoice["client_email"],
        "amount": invoice["amount"],
        "days_overdue": invoice["days_overdue"],
        "stage": stage_info["stage"],
        "tone": stage_info["tone"],
        "subject": email.get("subject", ""),
        "body": email.get("body", ""),
        "status": status
    }
    log.append(entry)
    save_log(log)
    print(f"  [LOG] {invoice['invoice_no']} → Stage {stage_info['stage']} ({status})")