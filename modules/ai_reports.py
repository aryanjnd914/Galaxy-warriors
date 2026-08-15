import urllib.request
import json
import time

GEMINI_API_KEY = "AQ.Ab8RN6Kptvox37W-3yL2C-UrstPJS52aCtYh4-ss7eOJ3mz-OA"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"

_cache = []

def generate_ai_threat_report(debris_obj):
    prompt = f"""You are an expert space debris analyst for ORBIT-GUARD mission control.
Generate a concise 3-sentence threat assessment for this debris object:
Name: {debris_obj.get("name", "UNKNOWN")}
Altitude: {debris_obj.get("perigee", "N/A")} km
Inclination: {debris_obj.get("inclination", "N/A")} degrees
Risk Level: {debris_obj.get("risk_level", "N/A")}
Risk Score: {debris_obj.get("risk_score", "N/A")}
Write in professional mission control style. Cover: current threat status, orbital decay risk, and recommended monitoring action."""

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Threat analysis unavailable: {str(e)}"

def generate_all_threat_reports(debris_list):
    global _cache
    if _cache:
        return _cache

    top6 = sorted(debris_list, key=lambda x: x.get("risk_score", 0), reverse=True)[:6]
    reports = []
    for obj in top6:
        report_text = generate_ai_threat_report(obj)
        reports.append({
            "name": obj.get("name", "UNKNOWN"),
            "risk_level": obj.get("risk_level", "N/A"),
            "altitude_km": obj.get("perigee", "N/A"),
            "risk_score": obj.get("risk_score", 0),
            "ai_report": report_text
        })
        time.sleep(4)

    _cache = reports
    return reports
