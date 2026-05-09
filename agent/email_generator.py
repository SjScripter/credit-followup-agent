import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=1000
)

def generate_email(invoice: dict, stage_info: dict) -> dict:
    system_prompt = """You are a professional finance communication assistant.
Your job is to write follow-up emails for overdue invoices.
Always personalise every email with the exact client name, invoice number,
amount, due date, and days overdue.
Return ONLY a JSON object with two keys: "subject" and "body".
No extra text, no markdown, no explanation."""

    user_prompt = f"""Write a follow-up email with the following details:

Client Name: {invoice['client_name']}
Invoice Number: {invoice['invoice_no']}
Amount Due: ₹{invoice['amount']}
Due Date: {invoice['due_date']}
Days Overdue: {invoice['days_overdue']}
Follow-Up Stage: {stage_info['label']}
Tone: {stage_info['tone']}
Call to Action: {stage_info['cta']}

Return ONLY a JSON object like this:
{{
  "subject": "email subject here",
  "body": "full email body here"
}}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)