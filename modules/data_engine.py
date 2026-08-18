import requests, json, os
from datetime import datetime, timedelta

CACHE_FILE = "data/cached_debris_tle.json"
API_URL = "https://api.keeptrack.space/v4/sats/brief"
API_KEY = "kt_demo_00000000000000000000000000"

MU = 398600.4418  # km^3/s^2
EARTH_R = 6371.0  # km

def parse_tle_params(tle1, tle2):
    try:
        inclination  = float(tle2[8:16].strip())
        eccentricity = float("0." + tle2[26:33].strip())
        mean_motion  = float(tle2[52:63].strip())  # revs/day
        raan         = float(tle2[17:25].strip())
        # Convert mean motion to rad/s
        n = mean_motion * 2 * 3.14159265 / 86400.0
        # Semi-major axis from Kepler's third law: a = (mu/n^2)^(1/3)
        semi_major   = (MU / (n * n)) ** (1.0/3.0)
        perigee      = semi_major * (1 - eccentricity) - EARTH_R
        apogee       = semi_major * (1 + eccentricity) - EARTH_R
        return inclination, eccentricity, round(perigee,1), round(apogee,1), mean_motion, 0.00015, raan
    except:
        return 74.0, 0.002, 500.0, 600.0, 14.3, 0.00015, 0.0

def fetch_live_tle():
    if os.path.exists(CACHE_FILE):
        mtime = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
        if datetime.now() - mtime < timedelta(hours=1):
            with open(CACHE_FILE) as f:
                cached = json.load(f)
            if cached and "tle_line1" in cached[0] and cached[0].get("perigee", -1) > 0:
                print(f"[data_engine] Using cached live data ({len(cached)} objects)")
                return cached

    try:
        print("[data_engine] Fetching LIVE data from KeepTrack API...")
        r = requests.get(API_URL, headers={"X-API-Key": API_KEY}, timeout=30)
        r.raise_for_status()
        all_objects = r.json()

        # Filter debris and deduplicate by name
        seen_names = set()
        debris = []
        for obj in all_objects:
            name = str(obj.get("name", "")).strip()
            if ("DEB" in name or "R/B" in name) and name not in seen_names:
                seen_names.add(name)
                debris.append(obj)
            if len(debris) >= 50:
                break

        result = []
        for d in debris:
            tle1 = d.get("tle1", "")
            tle2 = d.get("tle2", "")
            if not tle1 or not tle2:
                continue
            inc, ecc, perigee, apogee, mm, bstar, raan = parse_tle_params(tle1, tle2)
            # Skip objects with invalid orbits
            if perigee < 100 or perigee > 50000:
                continue
            result.append({
                "name":         d.get("name", "UNKNOWN DEB"),
                "norad_id":     tle1[2:7].strip() if tle1 else "00000",
                "tle_line1":    tle1,
                "tle_line2":    tle2,
                "inclination":  inc,
                "eccentricity": ecc,
                "perigee":      perigee,
                "apogee":       apogee,
                "mean_motion":  mm,
                "bstar":        bstar,
                "raan":         raan,
                "country":      d.get("country", "UNKNOWN"),
                "rcs":          float(d.get("rcs", 0.5) or 0.5),
                "fetched_live": True,
                "fetch_time":   datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            })
            if len(result) >= 50:
                break

        os.makedirs("data", exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(result, f, indent=2)

        print(f"[data_engine] LIVE fetch success — {len(result)} real-time debris objects at {datetime.utcnow().strftime('%H:%M UTC')}")
        return result

    except Exception as e:
        print(f"[data_engine] Live fetch failed: {e}")

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f:
                cached = json.load(f)
            if cached:
                print(f"[data_engine] Using cached data ({len(cached)} objects)")
                return cached
        except:
            pass

    print("[data_engine] ERROR: No data available")
    return []
