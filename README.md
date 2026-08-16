# ORBIT-GUARD: Space Debris Mission Control

> AI-powered space debris tracking, risk assessment, and removal planning system built for NSIC 2026.

## Live Demo
Run locally on edge hardware (Raspberry Pi 4 or laptop) — no cloud dependency.

## Features

| Module | Description |
|--------|-------------|
| Risk Scoring | Physics-based ML model — 5 orbital factors |
| Conjunction Analysis | Closest approach detection between debris pairs |
| Anomaly Detection | Isolation Forest — flags unusual decay patterns |
| Monte Carlo Simulation | 1000-run 24H/48H/72H collision probability |
| Decay Prediction | 30-day linear regression altitude forecast |
| AI Threat Reports | Gemini AI generates per-object assessments |
| Orbital Simulation | 3D Three.js visualization with mission planning |
| PDF Reports | Downloadable mission control reports |
| REST API | Full documented API at /api-docs |
| Unit Tests | 33 passing pytest tests validating all ML models |

## Tech Stack
- **Backend:** Python 3.14, Flask, Flask-SocketIO
- **ML/AI:** scikit-learn (Isolation Forest), Google Gemini API
- **Orbital Mechanics:** SGP4, real TLE data
- **Frontend:** HTML/CSS/JS, Chart.js, Three.js
- **Hardware:** Raspberry Pi 4 (edge node), Arduino Mega (LED alerts)

## Setup

```bash
git clone https://github.com/aryanjnd914/orbit-gaurd
cd orbit-gaurd
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Pages
| Page | URL |
|------|-----|
| Mission Control Dashboard | http://localhost:5000 |
| Orbital Simulation | http://localhost:5000/simulation |
| AI Threat Report | http://localhost:5000/report |
| API Documentation | http://localhost:5000/api-docs |
| PDF Download | http://localhost:5000/report/download |

## API Endpoints
| Endpoint | Description |
|----------|-------------|
| /api/debris | All 20 scored debris objects |
| /api/conjunctions | Top 10 closest approach pairs |
| /api/anomalies | Isolation Forest anomaly detection |
| /api/monte_carlo | 24H/48H/72H collision probabilities |
| /api/predictions | 30-day orbital decay predictions |
| /api/mission_queue | AI-ranked removal priority queue |
| /api/ai_reports | Gemini AI threat assessments |
| /api/sgp4 | Real-time SGP4 orbital positions |

## Run Tests
```bash
pytest tests.py -v
```
33 tests covering: risk scoring, anomaly detection, decay prediction, Monte Carlo, conjunction analysis.

## Real Debris Tracked
FENGYUN 1C DEB, IRIDIUM 33 DEB, COSMOS 2251 DEB, SL-16 R/B, CZ-4B R/B,
BREEZE-M DEB, THOR AGENA DEB, DELTA 1 DEB, COSMOS 954 DEB, and 11 more.

## Team
NSIC 2026 — Software Category — Team of 5

## Impact
Addresses Kessler Syndrome — protecting GPS, weather, and communications satellites
through AI-powered debris monitoring and removal planning.
