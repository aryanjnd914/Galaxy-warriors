import json

def compute_risk_score(obj):
    """
    Compute a physics-informed risk score (0.0 - 1.0) for a debris object.
    Higher score = higher collision risk.
    """
    # Factor 1: Altitude risk (LEO 400-800km is most congested)
    perigee = obj.get("perigee", 500)
    if 400 <= perigee <= 800:
        alt_risk = 1.0 - abs(perigee - 600) / 400
    elif perigee < 400:
        alt_risk = 0.4
    else:
        alt_risk = max(0.1, 1.0 - (perigee - 800) / 800)

    # Factor 2: Eccentricity risk (higher = crosses more orbital shells)
    ecc = obj.get("eccentricity", 0.001)
    ecc_risk = min(1.0, ecc / 0.005)

    # Factor 3: Inclination risk (polar/SSO orbits cross all others)
    inc = obj.get("inclination", 45)
    if 85 <= inc <= 100:
        inc_risk = 1.0
    elif 60 <= inc <= 85 or 100 <= inc <= 115:
        inc_risk = 0.7
    else:
        inc_risk = 0.4

    # Factor 4: Drag (bstar) - high drag = unstable orbit
    bstar = obj.get("bstar", 0.0001)
    drag_risk = min(1.0, bstar / 0.0005)

    # Factor 5: Mean motion - higher = lower orbit = more conjunctions
    mm = obj.get("mean_motion", 14.0)
    mm_risk = min(1.0, max(0.0, (mm - 13.0) / 3.0))

    # Weighted composite score
    score = (
        alt_risk  * 0.35 +
        ecc_risk  * 0.20 +
        inc_risk  * 0.25 +
        drag_risk * 0.10 +
        mm_risk   * 0.10
    )
    return round(min(1.0, max(0.0, score)), 4)

def classify_risk(score):
    if score > 0.90:
        return "CRITICAL"
    elif score > 0.75:
        return "HIGH"
    elif score > 0.55:
        return "MEDIUM"
    else:
        return "LOW"

def score_debris(debris_list):
    """Score and rank all debris objects. Returns sorted list."""
    results = []
    for obj in debris_list:
        score = compute_risk_score(obj)
        results.append({
            "name": obj["name"],
            "norad_id": obj["norad_id"],
            "inclination": obj.get("inclination", 0),
            "eccentricity": obj.get("eccentricity", 0),
            "perigee": obj.get("perigee", 0),
            "apogee": obj.get("apogee", 0),
            "mean_motion": obj.get("mean_motion", 0),
            "bstar": obj.get("bstar", 0),
            "raan": obj.get("raan", 0),
            "risk_score": score,
            "risk_percent": round(score * 100, 1),
            "risk_level": classify_risk(score),
            "priority_rank": 0
        })

    results.sort(key=lambda x: x["risk_score"], reverse=True)
    for i, r in enumerate(results):
        r["priority_rank"] = i + 1

    return results

if __name__ == "__main__":
    with open("data/cached_debris_tle.json") as f:
        debris = json.load(f)
    scored = score_debris(debris)
    print(f"Scored {len(scored)} objects\n")
    for obj in scored:
        print(f"#{obj['priority_rank']:2d} [{obj['risk_level']:8s}] {obj['risk_percent']:5.1f}%  {obj['name']}")