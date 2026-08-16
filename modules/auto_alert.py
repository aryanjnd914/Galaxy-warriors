"""
modules/auto_alert.py
Automated email alert system — sends notification when any debris object's
risk crosses a defined threshold (CRITICAL / HIGH).

Uses smtplib with Gmail SMTP. Requires a Gmail "App Password" (not your
normal password) since Gmail blocks plain password SMTP logins.

Setup (one time):
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app password for "Mail"
3. Put your email + app password in the CONFIG section below,
   or set them as environment variables (recommended for the public repo).
"""

import smtplib
import os
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ─── CONFIG ─────────────────────────────────────────────────────────────────
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.environ.get("ORBITGUARD_EMAIL", "youremail@gmail.com")
SENDER_APP_PASSWORD = os.environ.get("ORBITGUARD_EMAIL_PASSWORD", "your-app-password-here")
RECIPIENT_EMAILS = os.environ.get("ORBITGUARD_ALERT_RECIPIENTS", "youremail@gmail.com").split(",")

# Alert thresholds
ALERT_LEVELS = ["CRITICAL", "HIGH"]     # which risk levels trigger an alert
COOLDOWN_SECONDS = 1800                  # don't re-alert same object within 30 min

# State tracking — remembers which objects already triggered an alert recently
STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "alert_state.json")


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
    """Check cooldown — only alert once per object per COOLDOWN_SECONDS window."""
    state = _load_state()
    last_alert = state.get(str(norad_id))
    if last_alert is None:
        return True
    elapsed = time.time() - last_alert
    return elapsed > COOLDOWN_SECONDS


def _mark_alerted(norad_id):
    state = _load_state()
    state[str(norad_id)] = time.time()
    _save_state(state)


# ─── Email builder ──────────────────────────────────────────────────────────
def _build_email(objects):
    """Build a formatted HTML email for one or more triggering objects."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    rows = ""
    for obj in objects:
        color = "#ff4444" if obj["risk_level"] == "CRITICAL" else "#ff8800"
        rows += f"""
        <tr style="border-bottom:1px solid #333;">
          <td style="padding:8px;color:#eee;">{obj['name']}</td>
          <td style="padding:8px;color:{color};font-weight:bold;">{obj['risk_level']}</td>
          <td style="padding:8px;color:#aaa;">{obj.get('risk_percent', obj.get('risk_score','N/A'))}%</td>
          <td style="padding:8px;color:#aaa;">{obj.get('perigee','N/A')} km</td>
          <td style="padding:8px;color:#aaa;">#{obj.get('priority_rank','N/A')}</td>
        </tr>"""

    html = f"""
    <html>
    <body style="background:#0a0a1a;font-family:Arial,sans-serif;padding:20px;">
      <div style="max-width:600px;margin:0 auto;background:#111122;border:1px solid #ff444444;border-radius:10px;padding:24px;">
        <h2 style="color:#ff4444;margin-top:0;">🛰️ ORBIT-GUARD THREAT ALERT</h2>
        <p style="color:#aaa;font-size:13px;">Generated {now}</p>
        <p style="color:#ccc;">
          {len(objects)} object(s) have crossed the CRITICAL/HIGH risk threshold.
          Immediate review recommended.
        </p>
        <table style="width:100%;border-collapse:collapse;margin-top:16px;">
          <thead>
            <tr style="background:#1a1a2e;">
              <th style="padding:8px;text-align:left;color:#888;font-size:12px;">OBJECT</th>
              <th style="padding:8px;text-align:left;color:#888;font-size:12px;">RISK</th>
              <th style="padding:8px;text-align:left;color:#888;font-size:12px;">SCORE</th>
              <th style="padding:8px;text-align:left;color:#888;font-size:12px;">PERIGEE</th>
              <th style="padding:8px;text-align:left;color:#888;font-size:12px;">RANK</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        <p style="color:#555;font-size:11px;margin-top:20px;">
          This is an automated alert from ORBIT-GUARD Space Debris Mission Control.
          View the live dashboard at http://localhost:5000
        </p>
      </div>
    </body>
    </html>
    """
    return html


# ─── Main send function ─────────────────────────────────────────────────────
def send_email_alert(objects, subject=None):
    """
    Send an email alert for the given list of debris objects.
    objects: list of dicts with name, risk_level, risk_percent/risk_score, perigee, priority_rank
    Returns True on success, False on failure.
    """
    if not objects:
        return False

    if subject is None:
        crit_count = sum(1 for o in objects if o["risk_level"] == "CRITICAL")
        subject = f"🚨 ORBIT-GUARD ALERT: {crit_count} CRITICAL object(s) detected" if crit_count \
                  else f"⚠️ ORBIT-GUARD ALERT: {len(objects)} HIGH-risk object(s) detected"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENT_EMAILS)

    html_body = _build_email(objects)
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())
        print(f"[ALERT] Email sent for {len(objects)} object(s) → {RECIPIENT_EMAILS}")
        return True
    except Exception as e:
        print(f"[ALERT] Failed to send email: {e}")
        return False


# ─── Main check function — call this after scoring debris ─────────────────
def check_and_alert(scored_debris):
    """
    Scans scored debris list, finds objects crossing threshold that haven't
    alerted recently, and sends one batched email for all of them.

    scored_debris: list of debris dicts with 'risk_level', 'norad_id', etc.
    Returns number of objects alerted.
    """
    triggering = [
        obj for obj in scored_debris
        if obj.get("risk_level") in ALERT_LEVELS and _should_alert(obj.get("norad_id"))
    ]

    if not triggering:
        return 0

    success = send_email_alert(triggering)
    if success:
        for obj in triggering:
            _mark_alerted(obj["norad_id"])
        return len(triggering)
    return 0


if __name__ == "__main__":
    # Test with dummy data
    test_objects = [
        {"name": "FENGYUN 1C DEB", "norad_id": 29107, "risk_level": "CRITICAL",
         "risk_percent": 91.4, "perigee": 850, "priority_rank": 1},
        {"name": "COSMOS 2251 DEB", "norad_id": 34427, "risk_level": "HIGH",
         "risk_percent": 74.2, "perigee": 780, "priority_rank": 2},
    ]
    result = send_email_alert(test_objects)
    print("Test result:", result)
