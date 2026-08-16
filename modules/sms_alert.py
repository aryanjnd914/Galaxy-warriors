"""
modules/sms_alert.py
Automated SMS alert system — sends text message when debris crosses
CRITICAL/HIGH risk threshold.

Uses Twilio free trial (enough for demo).
Setup:
1. Sign up at https://www.twilio.com/try-twilio
2. Get Account SID, Auth Token, and a free Twilio number
3. Run: pip install twilio
4. Set environment variables (see below) OR fill in CONFIG section
"""

import os
import json
import time
from datetime import datetime

# ─── CONFIG — fill these in or set as environment variables ─────────────────
TWILIO_ACCOUNT_SID  = os.environ.get("TWILIO_SID",   "your_account_sid_here")
TWILIO_AUTH_TOKEN   = os.environ.get("TWILIO_TOKEN",  "your_auth_token_here")
TWILIO_FROM_NUMBER  = os.environ.get("TWILIO_FROM",   "+15551234567")  # your Twilio number
ALERT_TO_NUMBERS    = os.environ.get("TWILIO_TO",     "+919999999999").split(",")  # your phone

# Thresholds
ALERT_LEVELS     = ["CRITICAL", "HIGH"]
COOLDOWN_SECONDS = 1800   # 30 min — don't re-alert same object within this window

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "sms_alert_state.json")


# ─── State management ──────────────────────────────────────────────────────
def _load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _should_alert(norad_id):
    state = _load_state()
    last_alert = state.get(str(norad_id))
    if last_alert is None:
        return True
    return (time.time() - last_alert) > COOLDOWN_SECONDS


def _mark_alerted(norad_id):
    state = _load_state()
    state[str(norad_id)] = time.time()
    _save_state(state)


# ─── SMS builder ───────────────────────────────────────────────────────────
def _build_sms(objects):
    """Build concise SMS text — keep under 160 chars per segment."""
    now = datetime.utcnow().strftime("%H:%M UTC")
    crit = [o for o in objects if o["risk_level"] == "CRITICAL"]
    high = [o for o in objects if o["risk_level"] == "HIGH"]

    lines = [f"🛰 ORBIT-GUARD ALERT [{now}]"]

    if crit:
        lines.append(f"CRITICAL ({len(crit)}):")
        for o in crit[:3]:  # max 3 to keep SMS short
            score = o.get("risk_percent", o.get("risk_score", "?"))
            lines.append(f"  ⚠ {o['name']} — {score}% risk, perigee {o.get('perigee','?')}km")

    if high:
        lines.append(f"HIGH ({len(high)}):")
        for o in high[:2]:
            score = o.get("risk_percent", o.get("risk_score", "?"))
            lines.append(f"  ▲ {o['name']} — {score}% risk")

    lines.append("Dashboard: localhost:5000")
    return "\n".join(lines)


# ─── Send SMS ──────────────────────────────────────────────────────────────
def send_sms_alert(objects):
    """
    Send SMS to all numbers in ALERT_TO_NUMBERS.
    Returns True on success, False on failure.
    """
    if not objects:
        return False

    try:
        from twilio.rest import Client
    except ImportError:
        print("[SMS] Twilio not installed. Run: pip install twilio")
        return False

    if "your_account_sid_here" in TWILIO_ACCOUNT_SID:
        print("[SMS] Twilio credentials not configured — skipping SMS")
        return False

    message_body = _build_sms(objects)

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        for number in ALERT_TO_NUMBERS:
            number = number.strip()
            if not number:
                continue
            msg = client.messages.create(
                body=message_body,
                from_=TWILIO_FROM_NUMBER,
                to=number
            )
            print(f"[SMS] Sent to {number} — SID: {msg.sid}")
        return True

    except Exception as e:
        print(f"[SMS] Failed to send: {e}")
        return False


# ─── Main check — call after scoring debris ────────────────────────────────
def check_and_alert_sms(scored_debris):
    """
    Finds objects crossing threshold that haven't been alerted recently.
    Sends one batched SMS per check.
    Returns number of objects alerted.
    """
    triggering = [
        obj for obj in scored_debris
        if obj.get("risk_level") in ALERT_LEVELS
        and _should_alert(obj.get("norad_id"))
    ]

    if not triggering:
        print("[SMS] No new threshold crossings — no SMS sent")
        return 0

    success = send_sms_alert(triggering)
    if success:
        for obj in triggering:
            _mark_alerted(obj["norad_id"])
        print(f"[SMS] Alerted {len(triggering)} object(s)")
        return len(triggering)
    return 0


# ─── Flask endpoint helper ─────────────────────────────────────────────────
def manual_alert(scored_debris, norad_id=None):
    """
    Trigger a manual SMS alert from the dashboard.
    If norad_id given, alerts just that object.
    Otherwise alerts all CRITICAL/HIGH objects ignoring cooldown.
    """
    if norad_id:
        targets = [o for o in scored_debris if o.get("norad_id") == norad_id]
    else:
        targets = [o for o in scored_debris if o.get("risk_level") in ALERT_LEVELS]

    return send_sms_alert(targets)


if __name__ == "__main__":
    # Test with dummy data
    test_objects = [
        {"name": "FENGYUN 1C DEB",  "norad_id": 29107, "risk_level": "CRITICAL",
         "risk_percent": 91.4, "perigee": 850, "priority_rank": 1},
        {"name": "COSMOS 2251 DEB", "norad_id": 34427, "risk_level": "HIGH",
         "risk_percent": 74.2, "perigee": 780, "priority_rank": 2},
    ]
    print("SMS body preview:")
    print(_build_sms(test_objects))
    print("\nSending test SMS...")
    send_sms_alert(test_objects)
