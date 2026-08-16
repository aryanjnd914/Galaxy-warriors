import os
from twilio.rest import Client

sid   = os.environ.get("TWILIO_SID")
token = os.environ.get("TWILIO_TOKEN")
from_ = os.environ.get("TWILIO_FROM")
to    = os.environ.get("TWILIO_TO")

print(f"SID:   {sid}")
print(f"FROM:  {from_}")
print(f"TO:    {to}")

client = Client(sid, token)

try:
    msg = client.messages.create(
        body="ORBIT-GUARD ALERT: CRITICAL debris detected. Fengyun 1C at 850km perigee. Check mission control dashboard.",
        from_=from_,
        to=to
    )
    print(f"[SMS] SUCCESS! SID: {msg.sid}")
    print("Check your phone!")
except Exception as e:
    print(f"[SMS] Error: {e}")
