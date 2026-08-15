from sklearn.ensemble import IsolationForest
import numpy as np

def detect_anomalies(debris_list):
    """
    Use Isolation Forest to detect debris with unusual orbital decay patterns.
    Features: bstar (drag), eccentricity, mean_motion, perigee, inclination
    """
    if len(debris_list) < 4:
        return debris_list

    # Extract features
    features = []
    for obj in debris_list:
        features.append([
            float(obj.get('bstar', 0.0001)) * 10000,  # scale up small values
            float(obj.get('eccentricity', 0.001)) * 1000,
            float(obj.get('mean_motion', 14.0)),
            float(obj.get('perigee', 500)) / 100,
            float(obj.get('inclination', 51.6)) / 10,
        ])

    X = np.array(features)

    # Train Isolation Forest
    model = IsolationForest(
        n_estimators=100,
        contamination=0.2,  # expect ~20% anomalies
        random_state=42
    )
    model.fit(X)

    # Get predictions and anomaly scores
    predictions = model.predict(X)  # -1 = anomaly, 1 = normal
    scores = model.decision_function(X)  # lower = more anomalous

    # Normalize scores to 0-100 (higher = more anomalous)
    min_s, max_s = scores.min(), scores.max()
    if max_s != min_s:
        normalized = [(s - min_s) / (max_s - min_s) for s in scores]
    else:
        normalized = [0.5] * len(scores)
    anomaly_scores = [round((1 - n) * 100, 1) for n in normalized]

    # Add anomaly info to each debris object
    results = []
    for i, obj in enumerate(debris_list):
        obj_copy = dict(obj)
        obj_copy['is_anomaly'] = bool(predictions[i] == -1)
        obj_copy['anomaly_score'] = anomaly_scores[i]
        obj_copy['anomaly_label'] = '⚠ ANOMALY DETECTED' if predictions[i] == -1 else 'NORMAL'
        results.append(obj_copy)

    return results