"""
modules/voice_alert.py
Voice Alert System — speaks threat announcements using pyttsx3.
Uses Microsoft Hazel (British female) voice for mission control effect.
"""

import pyttsx3
import threading
import time

# ─── CONFIG ─────────────────────────────────────────────────────────────────
VOICE_INDEX   = 1        # 0=David, 1=Hazel(British), 2=Zira
SPEECH_RATE   = 148      # words per minute — 148 is clear and authoritative
SPEECH_VOLUME = 1.0      # 0.0 to 1.0

# Cooldown — don't repeat same object's alert within this many seconds
COOLDOWN_SECONDS = 120

_last_alerted = {}       # norad_id → timestamp
_speaking     = False    # prevent overlapping speech


# ─── Engine factory ──────────────────────────────────────────────────────────
def _get_engine():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if VOICE_INDEX < len(voices):
        engine.setProperty('voice', voices[VOICE_INDEX].id)
    engine.setProperty('rate',   SPEECH_RATE)
    engine.setProperty('volume', SPEECH_VOLUME)
    return engine


# ─── Core speak function ─────────────────────────────────────────────────────
def speak(text, blocking=False):
    """
    Speak text aloud.
    blocking=False runs in background thread so Flask doesn't freeze.
    """
    global _speaking
    if _speaking:
        return   # don't overlap

    def _run():
        global _speaking
        _speaking = True
        try:
            engine = _get_engine()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[VOICE] Error: {e}")
        finally:
            _speaking = False

    if blocking:
        _run()
    else:
        t = threading.Thread(target=_run, daemon=True)
        t.start()


# ─── Alert scripts ───────────────────────────────────────────────────────────
def announce_startup(object_count, critical_count):
    """Spoken on app startup."""
    text = (
        f"ORBIT-GUARD mission control online. "
        f"Tracking {object_count} debris objects. "
        f"{critical_count} objects classified as critical. "
        f"All systems nominal."
    )
    speak(text)


def announce_critical(obj):
    """Spoken when a CRITICAL object is detected."""
    name  = obj.get('name', 'Unknown object')
    score = obj.get('risk_percent', obj.get('risk_score', '?'))
    alt   = obj.get('perigee', '?')
    text  = (
        f"WARNING. CRITICAL debris detected. "
        f"{name}. "
        f"Risk score {score} percent. "
        f"Perigee altitude {alt} kilometres. "
        f"Immediate action required. "
        f"Initiating emergency response protocol."
    )
    speak(text)


def announce_high(obj):
    """Spoken when a HIGH risk object is detected."""
    name  = obj.get('name', 'Unknown object')
    score = obj.get('risk_percent', obj.get('risk_score', '?'))
    text  = (
        f"Alert. High risk debris detected. "
        f"{name}. "
        f"Risk score {score} percent. "
        f"Monitoring elevated threat."
    )
    speak(text)


def announce_conjunction(obj1_name, obj2_name, distance_km):
    """Spoken when two objects are dangerously close."""
    text = (
        f"Conjunction warning. "
        f"{obj1_name} and {obj2_name} "
        f"are approaching within {round(distance_km)} kilometres. "
        f"Collision probability elevated. "
        f"Ground station operators on standby."
    )
    speak(text)


def announce_mission_launch(target_name):
    """Spoken when removal mission is launched in simulation."""
    text = (
        f"Mission control to REMOVER ONE. "
        f"Initiating debris removal sequence. "
        f"Target: {target_name}. "
        f"Hohmann transfer orbit calculated. "
        f"Godspeed."
    )
    speak(text)


def announce_reentry(obj_name, days):
    """Spoken for imminent reentry objects."""
    text = (
        f"Reentry alert. "
        f"{obj_name} predicted atmospheric reentry in {days} days. "
        f"Ground track monitoring recommended. "
        f"Aviation authorities notified."
    )
    speak(text)


# ─── Main check — call after scoring ─────────────────────────────────────────
def check_and_announce(scored_debris):
    """
    Scans debris list and announces critical/high objects.
    Respects cooldown so it doesn't repeat every server restart.
    """
    now = time.time()

    for obj in scored_debris:
        norad = obj.get('norad_id')
        level = obj.get('risk_level', '')
        last  = _last_alerted.get(norad, 0)

        if (now - last) < COOLDOWN_SECONDS:
            continue

        if level == 'CRITICAL':
            announce_critical(obj)
            _last_alerted[norad] = now
            time.sleep(0.5)   # small gap between announcements
            break              # announce one at a time, highest first

        elif level == 'HIGH':
            announce_high(obj)
            _last_alerted[norad] = now
            time.sleep(0.5)
            break


if __name__ == "__main__":
    # Test all announcements
    print("Testing startup announcement...")
    announce_startup(20, 3)
    time.sleep(4)

    print("Testing critical alert...")
    announce_critical({
        'name': 'FENGYUN 1C DEB',
        'risk_percent': 91.4,
        'perigee': 850
    })
    time.sleep(6)

    print("Testing conjunction warning...")
    announce_conjunction('FENGYUN 1C DEB', 'COSMOS 2251 DEB', 76)
    time.sleep(5)

    print("Testing mission launch...")
    announce_mission_launch('FENGYUN 1C DEB')
    time.sleep(5)

    print("Testing reentry alert...")
    announce_reentry('PEGASUS DEB', 18)
    time.sleep(5)

    print("All voice tests complete.")
