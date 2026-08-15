from sgp4.api import Satrec, jday
from datetime import datetime
import math

# Cache so conjunction analysis only runs once per server session
_cache = None

def tle_to_satrec(obj):
    try:
        line1 = obj.get('tle_line1', '')
        line2 = obj.get('tle_line2', '')
        if line1 and line2:
            return Satrec.twoline2rv(line1, line2)
    except Exception:
        pass
    return None

def get_position(sat, dt):
    try:
        jd, fr = jday(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        e, r, v = sat.sgp4(jd, fr)
        if e == 0:
            return r
    except Exception:
        pass
    return None

def distance_3d(r1, r2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(r1, r2)))

def compute_conjunctions(debris_list, threshold_km=2000):
    global _cache
    if _cache is not None:
        return _cache

    conjunctions = []
    now = datetime.utcnow()

    positions = []
    for obj in debris_list:
        sat = tle_to_satrec(obj)
        if sat:
            pos = get_position(sat, now)
            if pos:
                positions.append((obj, pos))

    if len(positions) < 2:
        # Fallback — use perigee + inclination estimate
        for i in range(len(debris_list)):
            for j in range(i + 1, len(debris_list)):
                obj1 = debris_list[i]
                obj2 = debris_list[j]
                try:
                    alt1 = float(obj1.get('perigee', 500))
                    alt2 = float(obj2.get('perigee', 500))
                    inc1 = float(obj1.get('inclination', 51.6))
                    inc2 = float(obj2.get('inclination', 51.6))
                    alt_diff = abs(alt1 - alt2)
                    inc_diff = abs(inc1 - inc2)
                    estimated_dist = math.sqrt(alt_diff**2 + (inc_diff * 50)**2) + 50
                    risk = 'LOW'
                    if estimated_dist < 200:
                        risk = 'CRITICAL'
                    elif estimated_dist < 500:
                        risk = 'HIGH'
                    elif estimated_dist < 1000:
                        risk = 'MEDIUM'
                    conjunctions.append({
                        'object1': obj1.get('name', 'OBJ-A'),
                        'object2': obj2.get('name', 'OBJ-B'),
                        'distance_km': round(estimated_dist, 2),
                        'risk_level': risk,
                        'method': 'orbital_estimate'
                    })
                except Exception:
                    continue
    else:
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                obj1, pos1 = positions[i]
                obj2, pos2 = positions[j]
                dist = distance_3d(pos1, pos2)
                if dist < threshold_km:
                    risk = 'LOW'
                    if dist < 100:
                        risk = 'CRITICAL'
                    elif dist < 300:
                        risk = 'HIGH'
                    elif dist < 800:
                        risk = 'MEDIUM'
                    conjunctions.append({
                        'object1': obj1.get('name', 'OBJ-A'),
                        'object2': obj2.get('name', 'OBJ-B'),
                        'distance_km': round(dist, 2),
                        'risk_level': risk,
                        'method': 'sgp4'
                    })

    conjunctions.sort(key=lambda x: x['distance_km'])
    _cache = conjunctions[:10]
    return _cache

def compute_collision_probability(debris_list):
    results = []
    for obj in debris_list:
        try:
            alt = float(obj.get('perigee', 500))
            ecc = float(obj.get('eccentricity', 0.001))
            inc = float(obj.get('inclination', 51.6))
            base_prob = max(0.001, (800 - alt) / 60000)
            ecc_factor = 1 + ecc * 10
            inc_factor = 1 + (abs(inc - 51.6) / 180)
            probability = min(99.9, base_prob * ecc_factor * inc_factor * 100)
            results.append({
                'name': obj.get('name', 'UNKNOWN'),
                'collision_probability_percent': round(probability, 4)
            })
        except Exception:
            continue
    return sorted(results, key=lambda x: x['collision_probability_percent'], reverse=True)