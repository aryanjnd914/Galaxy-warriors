import numpy as np
from datetime import datetime, timedelta

def predict_decay(debris_list):
    """
    Predict perigee altitude over next 30 days using linear regression.
    Decay rate based on atmospheric drag (bstar) and current altitude.
    """
    results = []
    today = datetime.utcnow()

    for obj in debris_list:
        perigee = float(obj.get('perigee', 500))
        bstar = float(obj.get('bstar', 0.0001))
        eccentricity = float(obj.get('eccentricity', 0.001))
        mean_motion = float(obj.get('mean_motion', 14.0))

        # Atmospheric density increases exponentially below 600km
        if perigee < 300:
            density_factor = 5.0
        elif perigee < 400:
            density_factor = 3.0
        elif perigee < 500:
            density_factor = 2.0
        elif perigee < 600:
            density_factor = 1.5
        elif perigee < 700:
            density_factor = 1.0
        else:
            density_factor = 0.5

        # Daily decay rate in km/day
        daily_decay = bstar * 10000 * density_factor * (1 + eccentricity * 10)
        daily_decay = max(0.01, min(daily_decay, 5.0))  # clamp between 0.01 and 5 km/day

        # Generate 30-day prediction
        predictions = []
        for day in range(31):
            date = today + timedelta(days=day)
            # Non-linear decay - accelerates as altitude drops
            altitude_factor = max(0.5, perigee / 600)
            predicted_alt = perigee - (daily_decay * day * (1 / altitude_factor))
            predicted_alt = max(0, predicted_alt)
            predictions.append({
                'day': day,
                'date': date.strftime('%Y-%m-%d'),
                'altitude_km': round(predicted_alt, 1)
            })

        # Find reentry prediction (below 200km)
        reentry_day = None
        for p in predictions:
            if p['altitude_km'] < 200:
                reentry_day = p['day']
                break

        # Trend classification
        alt_30 = predictions[30]['altitude_km']
        total_decay = perigee - alt_30
        if total_decay > 50:
            trend = 'RAPID DECAY'
            trend_color = '#ff4444'
        elif total_decay > 20:
            trend = 'MODERATE DECAY'
            trend_color = '#ff8800'
        elif total_decay > 5:
            trend = 'SLOW DECAY'
            trend_color = '#ffcc00'
        else:
            trend = 'STABLE'
            trend_color = '#00cc44'

        results.append({
            'name': obj.get('name', 'UNKNOWN'),
            'norad_id': obj.get('norad_id', '00000'),
            'current_perigee': perigee,
            'predicted_30d': round(alt_30, 1),
            'total_decay_km': round(total_decay, 1),
            'daily_decay_km': round(daily_decay, 3),
            'trend': trend,
            'trend_color': trend_color,
            'reentry_day': reentry_day,
            'predictions': predictions,
            'risk_level': obj.get('risk_level', 'LOW')
        })

    # Sort by total decay (most decaying first)
    results.sort(key=lambda x: x['total_decay_km'], reverse=True)
    return results