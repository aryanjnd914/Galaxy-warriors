"""
modules/mission_queue.py
Auto Mission Queue — AI prioritizes debris removal order
without human input using multi-factor scoring.
"""

def compute_mission_queue(scored_debris, collision_probs=None, predictions=None, conjunctions=None):
    """
    Compute optimal debris removal queue using AI priority scoring.
    
    Factors:
    - Risk score (40%) — from ml_model.py
    - Collision probability (25%) — from conjunction analysis
    - Decay urgency (20%) — objects decaying soon need removal before reentry
    - Conjunction proximity (15%) — objects in active conjunction pairs
    
    Returns ranked list with mission metadata.
    """
    # Build lookup maps
    prob_map = {}
    if collision_probs:
        for p in collision_probs:
            prob_map[p.get('norad_id')] = p.get('collision_probability', 0)

    decay_map = {}
    if predictions:
        for p in predictions:
            # Objects decaying in < 30 days are urgent
            day = p.get('reentry_day', 999)
            if day is not None and day < 999:
                decay_map[p.get('norad_id')] = day

    # Objects in conjunction pairs get a boost
    conj_ids = set()
    if conjunctions:
        for c in conjunctions:
            conj_ids.add(str(c.get('obj1_norad', '')))
            conj_ids.add(str(c.get('obj2_norad', '')))

    queue = []
    for i, obj in enumerate(scored_debris):
        norad = str(obj.get('norad_id', ''))
        
        # Factor 1: Risk score (0-1)
        risk_score = obj.get('risk_score', 0)
        
        # Factor 2: Collision probability (0-1)
        col_prob = prob_map.get(norad, 0)
        
        # Factor 3: Decay urgency (0-1) — closer to reentry = higher score
        reentry_day = decay_map.get(norad, 999)
        if reentry_day < 999:
            decay_score = max(0, 1 - (reentry_day / 30))
        else:
            decay_score = 0
        
        # Factor 4: Conjunction proximity (0 or 1)
        conj_score = 1.0 if norad in conj_ids else 0.0
        
        # Weighted composite AI priority score
        ai_priority = (
            risk_score  * 0.40 +
            col_prob    * 0.25 +
            decay_score * 0.20 +
            conj_score  * 0.15
        )
        
        # Estimate mission parameters
        perigee = obj.get('perigee', 500)
        # Delta-v estimate (simplified Hohmann from 400km parking orbit)
        import math
        MU = 398600
        r1 = 400 + 6371
        r2 = perigee + 6371
        a_t = (r1 + r2) / 2
        v1 = math.sqrt(MU / r1)
        v_peri = math.sqrt(MU * (2/r1 - 1/a_t))
        v2 = math.sqrt(MU / r2)
        v_apo = math.sqrt(MU * (2/r2 - 1/a_t))
        delta_v = abs(v_peri - v1) + abs(v2 - v_apo)
        transit_min = math.pi * math.sqrt(a_t**3 / MU) / 60

        queue.append({
            "queue_rank": 0,  # filled after sort
            "norad_id": norad,
            "name": obj.get('name', 'UNKNOWN'),
            "risk_level": obj.get('risk_level', 'LOW'),
            "risk_percent": obj.get('risk_percent', 0),
            "ai_priority_score": round(ai_priority, 4),
            "ai_priority_percent": round(ai_priority * 100, 1),
            "risk_factor": round(risk_score * 0.40, 4),
            "collision_factor": round(col_prob * 0.25, 4),
            "decay_factor": round(decay_score * 0.20, 4),
            "conjunction_factor": round(conj_score * 0.15, 4),
            "perigee": perigee,
            "inclination": obj.get('inclination', 0),
            "delta_v_km_s": round(delta_v, 3),
            "transit_time_min": round(transit_min, 1),
            "reentry_day": reentry_day if reentry_day < 999 else None,
            "in_conjunction": norad in conj_ids,
            "status": "QUEUED"
        })

    # Sort by AI priority score descending
    queue.sort(key=lambda x: x['ai_priority_score'], reverse=True)
    
    # Assign queue ranks and cumulative mission time
    cumulative_time = 0
    for i, item in enumerate(queue):
        item['queue_rank'] = i + 1
        cumulative_time += item['transit_time_min'] + 15  # 15 min ops per object
        item['eta_minutes'] = round(cumulative_time, 0)

    return queue
