import pandas as pd
from datetime import date
from agent.escalation_engine import get_stage
from agent.email_generator import generate_email
from agent.audit_logger import log_email

def calculate_days_overdue(due_date_str: str) -> int:
    due_date = date.fromisoformat(due_date_str)
    today = date.today()
    delta = (today - due_date).days
    return max(delta, 0)

def run_agent(dry_run: bool = True):
    print("=" * 60)
    print("  CREDIT FOLLOW-UP EMAIL AGENT")
    print(f"  Today: {date.today()}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE SEND'}")
    print("=" * 60)

    df = pd.read_csv("data/invoices.csv")
    df["days_overdue"] = df["due_date"].apply(calculate_days_overdue)

    print(f"\n Loaded {len(df)} invoices\n")

    for _, row in df.iterrows():
        invoice = row.to_dict()
        print(f"🔍 Processing: {invoice['invoice_no']} | {invoice['client_name']} | {invoice['days_overdue']} days overdue")

        stage_info = get_stage(int(invoice["days_overdue"]))

        if stage_info is None:
            print(f"   Not overdue yet — skipping.\n")
            continue

        if stage_info["stage"] == 5:
            print(f"  🚨 FLAGGED FOR LEGAL REVIEW — no email sent.\n")
            log_email(invoice, stage_info, {"subject": "N/A", "body": "Flagged for legal review"}, status="flagged")
            continue

        print(f"    Generating {stage_info['tone']} email...")
        email = generate_email(invoice, stage_info)

        print(f"   Subject: {email['subject']}")
        print(f"   Preview: {email['body'][:100]}...")

        log_email(invoice, stage_info, email, status="dry-run" if dry_run else "sent")
        print()

    print("=" * 60)
    print("  ✅ AGENT RUN COMPLETE")
    print("  📁 Log saved to: logs/email_log.json")
    print("=" * 60)

if __name__ == "__main__":
    run_agent(dry_run=True)
