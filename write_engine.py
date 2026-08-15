content = '''import requests, json, os
from datetime import datetime, timedelta

CACHE_FILE = "data/cached_debris_tle.json"
GP_DEBRIS_URL = "https://celestrak.org/GP/query?GROUP=debris&FORMAT=json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OrbitGuard/1.0; student research)"}

FALLBACK_DATA = [
  {"name": "FENGYUN 1C DEB", "norad_id": "29228", "inclination": 98.6, "eccentricity": 0.0012, "mean_motion": 14.20, "perigee": 790, "apogee": 812, "bstar": 0.00021, "raan": 100.0},
  {"name": "IRIDIUM 33 DEB", "norad_id": "33778", "inclination": 86.4, "eccentricity": 0.0021, "mean_motion": 14.34, "perigee": 760, "apogee": 791, "bstar": 0.00019, "raan": 200.0},
  {"name": "COSMOS 2251 DEB", "norad_id": "34454", "inclination": 74.0, "eccentricity": 0.0015, "mean_motion": 14.28, "perigee": 770, "apogee": 802, "bstar": 0.00015, "raan": 150.0},
  {"name": "SL-16 R/B", "norad_id": "22285", "inclination": 71.0, "eccentricity": 0.0005, "mean_motion": 14.15, "perigee": 820, "apogee": 841, "bstar": 0.00005, "raan": 180.0},
  {"name": "CZ-4B R/B", "norad_id": "27601", "inclination": 98.0, "eccentricity": 0.0008, "mean_motion": 14.22, "perigee": 780, "apogee": 801, "bstar": 0.00008, "raan": 120.0},
  {"name": "BREEZE-M DEB", "norad_id": "39915", "inclination": 49.0, "eccentricity": 0.0031, "mean_motion": 13.90, "perigee": 400, "apogee": 901, "bstar": 0.00031, "raan": 90.0},
  {"name": "THOR AGENA DEB", "norad_id": "01642", "inclination": 99.1, "eccentricity": 0.0011, "mean_motion": 14.50, "perigee": 700, "apogee": 722, "bstar": 0.00011, "raan": 45.0},
  {"name": "DELTA 1 DEB", "norad_id": "06187", "inclination": 90.1, "eccentricity": 0.0020, "mean_motion": 14.10, "perigee": 840, "apogee": 871, "bstar": 0.00012, "raan": 270.0},
  {"name": "COSMOS 954 DEB", "norad_id": "10361", "inclination": 65.0, "eccentricity": 0.0018, "mean_motion": 14.05, "perigee": 850, "apogee": 880, "bstar": 0.00018, "raan": 310.0},
  {"name": "SL-8 R/B", "norad_id": "14820", "inclination": 74.1, "eccentricity": 0.0009, "mean_motion": 14.18, "perigee": 800, "apogee": 820, "bstar": 0.00009, "raan": 55.0},
  {"name": "PEGASUS DEB", "norad_id": "23106", "inclination": 28.5, "eccentricity": 0.0042, "mean_motion": 15.10, "perigee": 350, "apogee": 650, "bstar": 0.00042, "raan": 160.0},
  {"name": "STARSHINE 3 DEB", "norad_id": "26929", "inclination": 67.0, "eccentricity": 0.0006, "mean_motion": 14.60, "perigee": 680, "apogee": 700, "bstar": 0.00006, "raan": 220.0},
  {"name": "COSMOS 1275 DEB", "norad_id": "12607", "inclination": 82.9, "eccentricity": 0.0014, "mean_motion": 14.25, "perigee": 775, "apogee": 805, "bstar": 0.00014, "raan": 333.0},
  {"name": "ATLAS CENTAUR DEB", "norad_id": "03173", "inclination": 28.9, "eccentricity": 0.0033, "mean_motion": 13.75, "perigee": 920, "apogee": 980, "bstar": 0.00033, "raan": 77.0},
  {"name": "SL-3 R/B", "norad_id": "00733", "inclination": 65.1, "eccentricity": 0.0007, "mean_motion": 14.35, "perigee": 740, "apogee": 762, "bstar": 0.00007, "raan": 195.0},
  {"name": "COSMOS 3M R/B", "norad_id": "32957", "inclination": 83.0, "eccentricity": 0.0016, "mean_motion": 14.12, "perigee": 830, "apogee": 858, "bstar": 0.00016, "raan": 140.0},
  {"name": "ARIANE 1 DEB", "norad_id": "12378", "inclination": 51.6, "eccentricity": 0.0025, "mean_motion": 14.00, "perigee": 860, "apogee": 900, "bstar": 0.00025, "raan": 85.0},
  {"name": "TITAN 3C DEB", "norad_id": "08744", "inclination": 32.5, "eccentricity": 0.0038, "mean_motion": 13.80, "perigee": 910, "apogee": 970, "bstar": 0.00038, "raan": 250.0},
  {"name": "LACROSSE 5 DEB", "norad_id": "28646", "inclination": 57.0, "eccentricity": 0.0011, "mean_motion": 14.40, "perigee": 720, "apogee": 745, "bstar": 0.00011, "raan": 300.0},
  {"name": "RESURS DEB", "norad_id": "19650", "inclination": 97.8, "eccentricity": 0.0013, "mean_motion": 14.30, "perigee": 755, "apogee": 782, "bstar": 0.00013, "raan": 15.0}
]

def fetch_live_tle():
    # Always use cache if it exists — never overwrite with fewer objects
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cached = json.load(f)
        if len(cached) >= 20:
            print("[data_engine] Using cached TLE data")
            return cached

    # Try live API
    try:
        print("[data_engine] Trying CelesTrak GP JSON API...")
        resp = requests.get(GP_DEBRIS_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        gp_data = resp.json()
        debris_list = []
        for obj in gp_data[:100]:
            debris_list.append({
                "name": obj.get("OBJECT_NAME", "UNKNOWN DEB"),
                "norad_id": str(obj.get("NORAD_CAT_ID", "00000")),
                "inclination": float(obj.get("INCLINATION", 0)),
                "eccentricity": float(obj.get("ECCENTRICITY", 0)),
                "mean_motion": float(obj.get("MEAN_MOTION", 0)),
                "perigee": float(obj.get("PERIGEE", 400)),
                "apogee": float(obj.get("APOGEE", 500)),
                "bstar": float(obj.get("BSTAR", 0)),
                "raan": float(obj.get("RA_OF_ASC_NODE", 0)),
            })
        if len(debris_list) >= 20:
            os.makedirs("data", exist_ok=True)
            with open(CACHE_FILE, "w") as f:
                json.dump(debris_list, f, indent=2)
            print(f"[data_engine] Saved {len(debris_list)} live objects")
            return debris_list
    except Exception as e:
        print(f"[data_engine] Live fetch failed: {e}")

    # Use hardcoded fallback — never overwrite cache with this
    print("[data_engine] Using hardcoded fallback data")
    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(FALLBACK_DATA, f, indent=2)
    return FALLBACK_DATA
'''

with open('modules/data_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("data_engine.py written with 20 objects fallback")