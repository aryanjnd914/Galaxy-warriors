import random
import math

def run_monte_carlo(debris_list, simulations=1000):
    results = []

    for obj in debris_list:
        try:
            alt = float(obj.get("perigee", 500))
            inc = float(obj.get("inclination", 51.6))
            ecc = float(obj.get("eccentricity", 0.001))
            risk_score = float(obj.get("risk_score", 0.5))

            hits_24 = 0
            hits_48 = 0
            hits_72 = 0

            for _ in range(simulations):
                alt_var = alt + random.gauss(0, 2.0)
                inc_var = inc + random.gauss(0, 0.05)
                ecc_var = max(0, ecc + random.gauss(0, 0.0001))

                density_factor = max(0.1, (900 - alt_var) / 900)
                inc_factor = 1 + abs(math.sin(math.radians(inc_var))) * 0.5
                ecc_factor = 1 + ecc_var * 20

                base_prob = risk_score * density_factor * inc_factor * ecc_factor * 0.05

                if random.random() < base_prob * 1.0:
                    hits_24 += 1
                if random.random() < base_prob * 1.8:
                    hits_48 += 1
                if random.random() < base_prob * 2.5:
                    hits_72 += 1

            results.append({
                "name": obj.get("name", "UNKNOWN"),
                "norad_id": obj.get("norad_id", "N/A"),
                "risk_level": obj.get("risk_level", "N/A"),
                "altitude_km": alt,
                "prob_24h": round((hits_24 / simulations) * 100, 4),
                "prob_48h": round((hits_48 / simulations) * 100, 4),
                "prob_72h": round((hits_72 / simulations) * 100, 4),
                "simulations": simulations
            })

        except Exception:
            continue

    results.sort(key=lambda x: x["prob_72h"], reverse=True)
    return results
