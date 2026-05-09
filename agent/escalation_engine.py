def get_stage(days_overdue: int) -> dict:
    if days_overdue <= 0:
        return None
    elif 1 <= days_overdue <= 7:
        return {
            "stage": 1,
            "label": "1st Follow-Up",
            "tone": "Warm & Friendly",
            "cta": "Please use the payment link below to complete your payment."
        }
    elif 8 <= days_overdue <= 14:
        return {
            "stage": 2,
            "label": "2nd Follow-Up",
            "tone": "Polite but Firm",
            "cta": "Kindly confirm your payment date at the earliest."
        }
    elif 15 <= days_overdue <= 21:
        return {
            "stage": 3,
            "label": "3rd Follow-Up",
            "tone": "Formal & Serious",
            "cta": "Please respond within 48 hours to avoid further escalation."
        }
    elif 22 <= days_overdue <= 30:
        return {
            "stage": 4,
            "label": "4th Follow-Up",
            "tone": "Stern & Urgent",
            "cta": "Pay immediately or contact us to avoid legal escalation."
        }
    else:
        return {
            "stage": 5,
            "label": "Escalation Flag",
            "tone": "FLAG FOR LEGAL REVIEW",
            "cta": "Assign to finance manager — no auto email."
        }