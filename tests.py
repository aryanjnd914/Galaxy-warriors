import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.ml_model import compute_risk_score, classify_risk, score_debris
from modules.prediction import predict_decay
from modules.anomaly import detect_anomalies
from modules.conjunction import compute_conjunctions
from modules.monte_carlo import run_monte_carlo

# ─── Sample debris objects for testing ───────────────────────────────────────

SAMPLE_LOW = {
    "name": "TEST LOW RISK", "norad_id": "00001",
    "inclination": 28.5, "eccentricity": 0.0001,
    "mean_motion": 13.5, "perigee": 1200,
    "apogee": 1250, "bstar": 0.00001, "raan": 0.0
}

SAMPLE_CRITICAL = {
    "name": "TEST CRITICAL RISK", "norad_id": "00002",
    "inclination": 90.0, "eccentricity": 0.005,
    "mean_motion": 15.0, "perigee": 450,
    "apogee": 500, "bstar": 0.0005, "raan": 90.0
}

SAMPLE_HIGH = {
    "name": "TEST HIGH RISK", "norad_id": "00003",
    "inclination": 86.0, "eccentricity": 0.002,
    "mean_motion": 14.3, "perigee": 760,
    "apogee": 790, "bstar": 0.0002, "raan": 180.0
}

SAMPLE_DEBRIS_LIST = [SAMPLE_LOW, SAMPLE_CRITICAL, SAMPLE_HIGH,
    {"name": "FENGYUN 1C DEB", "norad_id": "29228", "inclination": 98.6,
     "eccentricity": 0.0012, "mean_motion": 14.20, "perigee": 790,
     "apogee": 812, "bstar": 0.00021, "raan": 100.0},
    {"name": "IRIDIUM 33 DEB", "norad_id": "33778", "inclination": 86.4,
     "eccentricity": 0.0021, "mean_motion": 14.34, "perigee": 760,
     "apogee": 791, "bstar": 0.00019, "raan": 200.0},
]

# ─── ML Model Tests ───────────────────────────────────────────────────────────

class TestRiskScoring:

    def test_risk_score_returns_float(self):
        score = compute_risk_score(SAMPLE_HIGH)
        assert isinstance(score, float)

    def test_risk_score_range(self):
        """Risk score must always be between 0 and 1."""
        for obj in SAMPLE_DEBRIS_LIST:
            score = compute_risk_score(obj)
            assert 0.0 <= score <= 1.0, f"Score out of range for {obj['name']}: {score}"

    def test_low_altitude_increases_risk(self):
        """Objects in congested LEO band (400-800km) score higher than very high orbits."""
        leo_alt = dict(SAMPLE_HIGH, perigee=600)   # peak congestion zone
        high_alt = dict(SAMPLE_HIGH, perigee=1200) # above congested zone
        assert compute_risk_score(leo_alt) > compute_risk_score(high_alt)

    def test_polar_orbit_increases_risk(self):
        """Polar orbit (90 deg) should score higher than equatorial."""
        polar = dict(SAMPLE_LOW, inclination=90.0)
        equatorial = dict(SAMPLE_LOW, inclination=5.0)
        assert compute_risk_score(polar) > compute_risk_score(equatorial)

    def test_high_drag_increases_risk(self):
        """Higher bstar drag coefficient should increase risk."""
        high_drag = dict(SAMPLE_LOW, bstar=0.001)
        low_drag = dict(SAMPLE_LOW, bstar=0.00001)
        assert compute_risk_score(high_drag) > compute_risk_score(low_drag)

    def test_high_eccentricity_increases_risk(self):
        """Higher eccentricity crosses more orbital shells."""
        high_ecc = dict(SAMPLE_LOW, eccentricity=0.008)
        low_ecc = dict(SAMPLE_LOW, eccentricity=0.0001)
        assert compute_risk_score(high_ecc) > compute_risk_score(low_ecc)

    def test_classify_risk_critical(self):
        assert classify_risk(0.80) == "CRITICAL"

    def test_classify_risk_high(self):
        assert classify_risk(0.60) == "HIGH"

    def test_classify_risk_medium(self):
        assert classify_risk(0.40) == "MEDIUM"

    def test_classify_risk_low(self):
        assert classify_risk(0.20) == "LOW"

    def test_classify_risk_boundaries(self):
        assert classify_risk(0.76) == "CRITICAL"   # above 0.75 threshold
        assert classify_risk(0.75) == "HIGH"        # exactly 0.75 = HIGH not CRITICAL
        assert classify_risk(0.51) == "HIGH"
        assert classify_risk(0.50) == "MEDIUM"      # exactly 0.50 = MEDIUM (threshold is > 0.50)
        assert classify_risk(0.499) == "MEDIUM"
        assert classify_risk(0.25) == "LOW"         # exactly 0.25 = LOW (threshold is > 0.25)
        assert classify_risk(0.249) == "LOW"

# ─── score_debris Tests ───────────────────────────────────────────────────────

class TestScoreDebris:

    def test_returns_list(self):
        result = score_debris(SAMPLE_DEBRIS_LIST)
        assert isinstance(result, list)

    def test_correct_length(self):
        result = score_debris(SAMPLE_DEBRIS_LIST)
        assert len(result) == len(SAMPLE_DEBRIS_LIST)

    def test_required_fields_present(self):
        result = score_debris(SAMPLE_DEBRIS_LIST)
        required = ["name", "norad_id", "risk_score", "risk_percent",
                    "risk_level", "priority_rank"]
        for obj in result:
            for field in required:
                assert field in obj, f"Missing field: {field}"

    def test_sorted_by_risk_descending(self):
        result = score_debris(SAMPLE_DEBRIS_LIST)
        scores = [r["risk_score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_priority_rank_sequential(self):
        result = score_debris(SAMPLE_DEBRIS_LIST)
        ranks = [r["priority_rank"] for r in result]
        assert ranks == list(range(1, len(result) + 1))

    def test_risk_percent_matches_score(self):
        result = score_debris(SAMPLE_DEBRIS_LIST)
        for obj in result:
            assert abs(obj["risk_percent"] - obj["risk_score"] * 100) < 0.1

# ─── Anomaly Detection Tests ──────────────────────────────────────────────────

class TestAnomalyDetection:

    def test_returns_list(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = detect_anomalies(scored)
        assert isinstance(result, list)

    def test_anomaly_fields_present(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = detect_anomalies(scored)
        for obj in result:
            assert "is_anomaly" in obj
            assert "anomaly_score" in obj
            assert "anomaly_label" in obj

    def test_anomaly_score_range(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = detect_anomalies(scored)
        for obj in result:
            assert 0.0 <= obj["anomaly_score"] <= 100.0

    def test_is_anomaly_boolean(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = detect_anomalies(scored)
        for obj in result:
            assert isinstance(obj["is_anomaly"], bool)

# ─── Decay Prediction Tests ───────────────────────────────────────────────────

class TestDecayPrediction:

    def test_returns_list(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = predict_decay(scored)
        assert isinstance(result, list)

    def test_prediction_fields_present(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = predict_decay(scored)
        for obj in result:
            assert "current_perigee" in obj
            assert "predicted_30d" in obj
            assert "total_decay_km" in obj
            assert "trend" in obj
            assert "daily_decay_km" in obj

    def test_predicted_altitude_lower_than_current(self):
        """Predicted altitude must always be <= current."""
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = predict_decay(scored)
        for obj in result:
            assert obj["predicted_30d"] <= obj["current_perigee"]

    def test_low_altitude_decays_faster(self):
        """Lower altitude objects should decay faster."""
        low = score_debris([dict(SAMPLE_HIGH, perigee=350, bstar=0.0005)])
        high = score_debris([dict(SAMPLE_HIGH, perigee=900, bstar=0.0001)])
        low_pred = predict_decay(low)[0]
        high_pred = predict_decay(high)[0]
        assert low_pred["daily_decay_km"] >= high_pred["daily_decay_km"]

    def test_trend_valid_values(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = predict_decay(scored)
        valid_trends = {"RAPID DECAY", "MODERATE DECAY", "SLOW DECAY", "STABLE"}
        for obj in result:
            assert obj["trend"] in valid_trends

# ─── Monte Carlo Tests ────────────────────────────────────────────────────────

class TestMonteCarlo:

    def test_returns_list(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = run_monte_carlo(scored)
        assert isinstance(result, list)

    def test_probability_fields_present(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = run_monte_carlo(scored)
        for obj in result:
            assert "prob_24h" in obj
            assert "prob_48h" in obj
            assert "prob_72h" in obj

    def test_probabilities_non_negative(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = run_monte_carlo(scored)
        for obj in result:
            assert obj["prob_24h"] >= 0
            assert obj["prob_48h"] >= 0
            assert obj["prob_72h"] >= 0

# ─── Conjunction Tests ────────────────────────────────────────────────────────

class TestConjunction:

    def test_returns_list(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = compute_conjunctions(scored)
        assert isinstance(result, list)

    def test_conjunction_fields(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = compute_conjunctions(scored)
        for c in result:
            assert "object1" in c
            assert "object2" in c
            assert "distance_km" in c
            assert "risk_level" in c

    def test_sorted_by_distance(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = compute_conjunctions(scored)
        distances = [c["distance_km"] for c in result]
        assert distances == sorted(distances)

    def test_no_self_conjunction(self):
        scored = score_debris(SAMPLE_DEBRIS_LIST)
        result = compute_conjunctions(scored)
        for c in result:
            assert c["object1"] != c["object2"]
