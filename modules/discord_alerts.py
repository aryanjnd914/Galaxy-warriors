import urllib.request
import json
from datetime import datetime

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1538496929019985962/2Nkr2I9V3fMWBsGCu-Y9CE2stRWiAxbVRiq2I9YgsDFTEg28RhEo08UlODmvEDF4ze-y"

def send_discord_alert(title, message, color=15158332):
    payload = json.dumps({
        "username": "ORBIT-GUARD Mission Control",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/1998/1998592.png",
        "embeds": [{
            "title": title,
            "description": message,
            "color": color,
            "footer": {
                "text": f"ORBIT-GUARD v2.0 | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            }
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        urllib.request.urlopen(req, timeout=10)
        return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def send_critical_alert(debris_obj):
    name = debris_obj.get("name", "UNKNOWN")
    risk = debris_obj.get("risk_level", "N/A")
    alt = debris_obj.get("perigee", "N/A")
    score = debris_obj.get("risk_percent", "N/A")
    inc = debris_obj.get("inclination", "N/A")

    title = f"🚨 CRITICAL DEBRIS ALERT — {name}"
    message = (
        f"**Object:** {name}\n"
        f"**Risk Level:** {risk}\n"
        f"**Risk Score:** {score}%\n"
        f"**Altitude:** {alt} km\n"
        f"**Inclination:** {inc}°\n"
        f"**Status:** IMMEDIATE MONITORING REQUIRED\n\n"
        f"⚠️ This object poses an elevated collision threat to active satellites."
    )
    return send_discord_alert(title, message, color=15158332)


def send_conjunction_alert(conj):
    obj1 = conj.get("object1", "OBJ-A")
    obj2 = conj.get("object2", "OBJ-B")
    dist = conj.get("distance_km", "N/A")
    risk = conj.get("risk_level", "N/A")

    title = f"⚠️ CONJUNCTION WARNING — {obj1} ↔ {obj2}"
    message = (
        f"**Object 1:** {obj1}\n"
        f"**Object 2:** {obj2}\n"
        f"**Distance:** {dist} km apart\n"
        f"**Risk Level:** {risk}\n\n"
        f"🛸 Two debris objects are in close proximity. Collision avoidance recommended."
    )
    color = 15158332 if risk == "CRITICAL" else 16744272
    return send_discord_alert(title, message, color=color)


def send_status_report(debris_list, conjunctions):
    critical = sum(1 for d in debris_list if d.get("risk_level") == "CRITICAL")
    high = sum(1 for d in debris_list if d.get("risk_level") == "HIGH")
    total = len(debris_list)
    conj_count = len(conjunctions)

    title = "📡 ORBIT-GUARD STATUS REPORT"
    message = (
        f"**Total Objects Tracked:** {total}\n"
        f"**Critical Risk:** {critical}\n"
        f"**High Risk:** {high}\n"
        f"**Active Conjunctions:** {conj_count}\n\n"
        f"🌍 ORBIT-GUARD Mission Control is actively monitoring all debris objects."
    )
    color = 15158332 if critical > 0 else 3066993
    return send_discord_alert(title, message, color=color)
