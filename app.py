import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from agent.escalation_engine import get_stage
from agent.email_generator import generate_email
from agent.audit_logger import log_email

st.set_page_config(
    page_title="Credit Follow-Up Agent",
    page_icon="💰",
    layout="wide"
)

def calculate_days_overdue(due_date_str: str) -> int:
    due_date = date.fromisoformat(due_date_str)
    today = date.today()
    return max((today - due_date).days, 0)

def load_invoices():
    df = pd.read_csv("data/invoices.csv")
    df["days_overdue"] = df["due_date"].apply(calculate_days_overdue)
    return df

def stage_badge(days):
    if days <= 0:
        return "Not Overdue"
    elif days <= 7:
        return "Stage 1 - Warm"
    elif days <= 14:
        return "Stage 2 - Firm"
    elif days <= 21:
        return "Stage 3 - Formal"
    elif days <= 30:
        return "Stage 4 - Urgent"
    else:
        return "LEGAL FLAG"

df = load_invoices()

# ── Header ────────────────────────────────────────────────
st.title("Credit Follow-Up Email Agent")
st.caption(f"AI-powered overdue invoice follow-up system — TCI Finance Team | Today: {date.today()}")
st.divider()

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.title("Controls")
dry_run = st.sidebar.toggle("Dry Run Mode", value=True)
if dry_run:
    st.sidebar.success("Dry Run ON — no real emails sent")
else:
    st.sidebar.warning("Live Mode — emails will be sent!")

st.sidebar.divider()
st.sidebar.markdown("### Summary")
overdue = df[df["days_overdue"] > 0]
st.sidebar.metric("Total Invoices", len(df))
st.sidebar.metric("Overdue", len(overdue))
st.sidebar.metric("Flagged for Legal", len(df[df["days_overdue"] > 30]))
st.sidebar.metric("Total Outstanding", f"Rs.{df['amount'].sum():,}")

# ── Invoice Table ─────────────────────────────────────────
st.subheader("Invoice Queue")
display_df = df.copy()
display_df["Stage"] = display_df["days_overdue"].apply(stage_badge)
display_df["Amount (Rs.)"] = display_df["amount"].apply(lambda x: f"Rs.{x:,}")
st.dataframe(
    display_df[["invoice_no", "client_name", "client_email", "Amount (Rs.)", "due_date", "days_overdue", "Stage"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "invoice_no": "Invoice No.",
        "client_name": "Client",
        "client_email": "Email",
        "due_date": "Due Date",
        "days_overdue": "Days Overdue",
    }
)

st.divider()

# ── Run Agent ─────────────────────────────────────────────
st.subheader("Run Agent")
col1, col2 = st.columns([1, 1])
with col1:
    run_btn = st.button("Run Agent", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("Clear Logs", use_container_width=True)

if clear_btn:
    if os.path.exists("logs/email_log.json"):
        os.remove("logs/email_log.json")
        st.success("Logs cleared!")
        st.rerun()

if run_btn:
    st.divider()
    st.subheader("Processing Invoices...")
    progress = st.progress(0)
    total = len(df)

    for i, (_, row) in enumerate(df.iterrows()):
        invoice = row.to_dict()
        stage_info = get_stage(int(invoice["days_overdue"]))
        progress.progress((i + 1) / total)

        with st.expander(
            f"{invoice['invoice_no']} — {invoice['client_name']} ({invoice['days_overdue']} days overdue)",
            expanded=True
        ):
            if stage_info is None:
                st.success("Not overdue yet — skipped")
                continue

            if stage_info["stage"] == 5:
                st.error("FLAGGED FOR LEGAL REVIEW — No email sent")
                log_email(invoice, stage_info, {"subject": "N/A", "body": "Flagged for legal review"}, status="flagged")
                continue

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Stage:** {stage_info['label']}")
                st.markdown(f"**Tone:** {stage_info['tone']}")
            with col_b:
                st.markdown(f"**Amount:** Rs.{invoice['amount']:,}")
                st.markdown(f"**Due Date:** {invoice['due_date']}")

            with st.spinner("Generating email via AI..."):
                email = generate_email(invoice, stage_info)

            st.markdown(f"**Subject:** `{email['subject']}`")
            st.text_area("Email Body", email["body"], height=200, key=f"email_{i}")

            status = "dry-run" if dry_run else "sent"
            log_email(invoice, stage_info, email, status=status)

            if dry_run:
                st.info("Logged as dry-run — not sent")
            else:
                st.success("Email sent!")

    progress.progress(100)
    st.success("Agent run complete!")
    st.rerun()

st.divider()

# ── Audit Log ─────────────────────────────────────────────
st.subheader("Audit Log")

if os.path.exists("logs/email_log.json"):
    with open("logs/email_log.json", "r") as f:
        logs = json.load(f)

    if logs:
        log_df = pd.DataFrame(logs)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Logged", len(log_df))
        c2.metric("Dry Run", len(log_df[log_df["status"] == "dry-run"]))
        c3.metric("Sent", len(log_df[log_df["status"] == "sent"]))
        c4.metric("Flagged", len(log_df[log_df["status"] == "flagged"]))

        st.dataframe(
            log_df[["timestamp", "invoice_no", "client_name", "stage", "tone", "subject", "status"]],
            use_container_width=True,
            hide_index=True
        )

        with st.expander("View All Generated Emails"):
            for i, log in enumerate(logs):
                st.markdown("---")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Invoice:** {log['invoice_no']}")
                    st.markdown(f"**Client:** {log['client_name']}")
                    st.markdown(f"**Email:** {log['client_email']}")
                    st.markdown(f"**Amount:** Rs.{log['amount']:,}")
                with col_b:
                    st.markdown(f"**Stage:** {log['stage']}")
                    st.markdown(f"**Tone:** {log['tone']}")
                    st.markdown(f"**Days Overdue:** {log['days_overdue']}")
                    st.markdown(f"**Status:** `{log['status']}`")
                if log["status"] != "flagged":
                    st.markdown(f"**Subject:** `{log['subject']}`")
                    st.text_area("Body", log["body"], height=150, key=f"view_email_{i}")
                else:
                    st.error("Flagged for legal review — no email generated")
                st.markdown(f"*Logged at: {log['timestamp']}*")

        st.download_button(
            label="Download Full Log (JSON)",
            data=json.dumps(logs, indent=2),
            file_name="email_audit_log.json",
            mime="application/json"
        )
    else:
        st.info("No logs yet — run the agent first!")
else:
    st.info("No logs yet — run the agent first!")