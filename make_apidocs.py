with open("templates/api_docs.html", "w", encoding="utf-8") as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ORBIT-GUARD API Documentation</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #050510; color: #fff; font-family: monospace; }
.header { background: #0a0a1a; border-bottom: 1px solid #00ccff; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
.header h1 { color: #00ccff; font-size: 1.5rem; }
.header a { color: #888; text-decoration: none; font-size: 0.85rem; }
.header a:hover { color: #00ccff; }
.container { max-width: 1100px; margin: 0 auto; padding: 40px 20px; }
.intro { background: #0d0d1a; border: 1px solid #00ccff; border-radius: 12px; padding: 24px; margin-bottom: 32px; }
.intro h2 { color: #00ccff; margin-bottom: 8px; }
.intro p { color: #888; line-height: 1.7; font-size: 0.9rem; }
.base-url { background: #050510; border: 1px solid #333; border-radius: 6px; padding: 10px 16px; margin-top: 12px; color: #00ff88; font-size: 0.95rem; }
.endpoint { background: #0d0d1a; border: 1px solid #1a1a3a; border-radius: 12px; padding: 24px; margin-bottom: 20px; transition: border-color 0.2s; }
.endpoint:hover { border-color: #00ccff; }
.endpoint-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.method { padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }
.get { background: #003322; color: #00ff88; border: 1px solid #00ff88; }
.endpoint-path { color: #fff; font-size: 1rem; font-weight: bold; }
.endpoint-desc { color: #888; font-size: 0.88rem; margin-bottom: 16px; line-height: 1.6; }
.response-box { background: #050510; border: 1px solid #333; border-radius: 8px; padding: 16px; font-size: 0.82rem; overflow-x: auto; }
.response-box pre { color: #00ff88; line-height: 1.6; }
.try-btn { background: transparent; border: 1px solid #00ccff; color: #00ccff; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-family: monospace; font-size: 0.82rem; margin-top: 12px; }
.try-btn:hover { background: #00ccff; color: #000; }
.response-live { background: #050510; border: 1px solid #00ff88; border-radius: 8px; padding: 16px; margin-top: 10px; display: none; }
.response-live pre { color: #00ff88; font-size: 0.8rem; max-height: 300px; overflow-y: auto; line-height: 1.5; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-left: 8px; }
.tag-live { background: #003322; color: #00ff88; border: 1px solid #00ff88; }
.tag-ml { background: #1a0030; color: #cc88ff; border: 1px solid #cc88ff; }
.tag-ai { background: #1a1a00; color: #ffcc00; border: 1px solid #ffcc00; }
.section-title { color: #00ccff; font-size: 1.1rem; margin: 32px 0 16px 0; border-bottom: 1px solid #1a1a3a; padding-bottom: 8px; }
</style>
</head>
<body>
<div class="header">
  <h1>&#128752; ORBIT-GUARD REST API</h1>
  <div>
    <a href="/">&#8592; Mission Control</a> &nbsp;|&nbsp;
    <a href="/simulation">Simulation</a> &nbsp;|&nbsp;
    <a href="/report">Report</a>
  </div>
</div>

<div class="container">
  <div class="intro">
    <h2>API Documentation</h2>
    <p>ORBIT-GUARD exposes a full REST API for real-time space debris tracking, risk assessment, and conjunction analysis. All endpoints return JSON. No authentication required for read-only access.</p>
    <div class="base-url">Base URL: http://localhost:5000</div>
  </div>

  <div class="section-title">&#127760; Core Debris Endpoints</div>

  <div class="endpoint">
    <div class="endpoint-header">
      <span class="method get">GET</span>
      <span class="endpoint-path">/api/debris</span>
      <span class="tag tag-live">LIVE</span>
      <span class="tag tag-ml">ML SCORED</span>
    </div>
    <div class="endpoint-desc">Returns all tracked debris objects with physics-based ML risk scores. Each object includes orbital parameters, risk classification (CRITICAL/HIGH/MEDIUM/LOW), and priority ranking.</div>
    <div class="response-box">
      <pre>[
  {
    "name": "DELTA 1 DEB",
    "norad_id": "06187",
    "risk_level": "HIGH",
    "risk_score": 0.7232,
    "risk_percent": 72.3,
    "perigee": 840,
    "apogee": 870,
    "inclination": 90.1,
    "eccentricity": 0.002,
    "mean_motion": 14.1,
    "priority_rank": 1
  }, ...
]</pre>
    </div>
    <button class="try-btn" onclick="tryApi('/api/debris', 'res-debris')">&#9654; Try it live</button>
    <div class="response-live" id="res-debris"><pre id="res-debris-data">Loading...</pre></div>
  </div>

  <div class="endpoint">
    <div class="endpoint-header">
      <span class="method get">GET</span>
      <span class="endpoint-path">/api/risk/&lt;norad_id&gt;</span>
      <span class="tag tag-ml">ML SCORED</span>
    </div>
    <div class="endpoint-desc">Returns detailed risk assessment for a single debris object by NORAD ID. Example: /api/risk/06187 returns DELTA 1 DEB data.</div>
    <div class="response-box">
      <pre>{
  "name": "DELTA 1 DEB",
  "norad_id": "06187",
  "risk_level": "HIGH",
  "risk_score": 0.7232,
  "risk_percent": 72.3,
  "perigee": 840,
  "inclination": 90.1
}</pre>
    </div>
    <button class="try-btn" onclick="tryApi('/api/risk/06187', 'res-risk')">&#9654; Try it live</button>
    <div class="response-live" id="res-risk"><pre id="res-risk-data">Loading...</pre></div>
  </div>

  <div class="endpoint">
    <div class="endpoint-header">
      <span class="method get">GET</span>
      <span class="endpoint-path">/api/conjunctions</span>
      <span class="tag tag-live">LIVE</span>
    </div>
    <div class="endpoint-desc">Returns all active conjunction pairs — debris objects within 2000km of each other. Sorted by closest approach distance. Uses SGP4 orbital mechanics for position computation.</div>
    <div class="response-box">
      <pre>[
  {
    "object1": "THOR AGENA DEB",
    "object2": "FENGYUN 1C DEB",
    "distance_km": 75.0,
    "risk_level": "CRITICAL",
    "method": "orbital_estimate"
  }, ...
]</pre>
    </div>
    <button class="try-btn" onclick="tryApi('/api/conjunctions', 'res-conj')">&#9654; Try it live</button>
    <div class="response-live" id="res-conj"><pre id="res-conj-data">Loading...</pre></div>
  </div>

  <div class="section-title">&#129302; AI & ML Endpoints</div>

  <div class="endpoint">
    <div class="endpoint-header">
      <span class="method get">GET</span>
      <span class="endpoint-path">/api/monte_carlo</span>
      <span class="tag tag-ml">1000 SIMULATIONS</span>
    </div>
    <div class="endpoint-desc">Runs Monte Carlo simulation (1000 iterations) varying orbital parameters within uncertainty bounds. Returns collision probability for 24h, 48h, and 72h windows.</div>
    <div class="response-box">
      <pre>[
  {
    "name": "PEGASUS DEB",
    "prob_24h": 2.1,
    "prob_48h": 3.8,
    "prob_72h": 5.2,
    "simulations": 1000
  }, ...
]</pre>
    </div>
    <button class="try-btn" onclick="tryApi('/api/monte_carlo', 'res-mc')">&#9654; Try it live</button>
    <div class="response-live" id="res-mc"><pre id="res-mc-data">Loading...</pre></div>
  </div>

  <div class="endpoint">
    <div class="endpoint-header">
      <span class="method get">GET</span>
      <span class="endpoint-path">/api/anomalies</span>
      <span class="tag tag-ml">ISOLATION FOREST</span>
    </div>
    <div class="endpoint-desc">Uses scikit-learn Isolation Forest algorithm to detect debris objects with unusual orbital decay patterns. Flags objects behaving differently from the population.</div>
    <div class="response-box">
      <pre>[
  {
    "name": "BREEZE-M DEB",
    "anomaly": true,
    "anomaly_score": -0.142
  }, ...
]</pre>
    </div>
    <button class="try-btn" onclick="tryApi('/api/anomalies', 'res-anom')">&#9654; Try it live</button>
    <div class="response-live" id="res-anom"><pre id="res-anom-data">Loading...</pre></div>
  </div>

  <div class="endpoint">
    <div class="endpoint-header">
      <span class="method get">GET</span>
      <span class="endpoint-path">/api/predictions</span>
      <span class="tag tag-ml">30-DAY FORECAST</span>
    </div>
    <div class="endpoint-desc">Predicts perigee altitude decay over next 30 days using atmospheric drag modeling. Returns day-by-day altitude predictions and estimated reentry date.</div>
    <div class="response-box">
      <pre>[
  {
    "name": "PEGASUS DEB",
    "reentry_day": 18,
    "decay_rate_km_per_day": 2.1,
    "altitudes": [350, 347, 344, ...]
  }, ...
]</pre>
    </div>
    <button class="try-btn" onclick="tryApi('/api/predictions', 'res-pred')">&#9654; Try it live</button>
    <div class="response-live" id="res-pred"><pre id="res-pred-data">Loading...</pre></div>
  </div>

  <div class="endpoint">
    <div class="endpoint-header">
      <span class="method get">GET</span>
      <span class="endpoint-path">/api/mission_queue</span>
      <span class="tag tag-ai">AI RANKED</span>
    </div>
    <div class="endpoint-desc">Returns AI-prioritized debris removal mission queue for REMOVER-1 spacecraft. Includes Hohmann transfer Δv calculations, transit times, and ETA for each target.</div>
    <div class="response-box">
      <pre>[
  {
    "queue_rank": 1,
    "name": "PEGASUS DEB",
    "ai_priority_percent": 30.5,
    "delta_v_km_s": 0.028,
    "eta_minutes": 61,
    "transit_time_min": 46,
    "status": "QUEUED"
  }, ...
]</pre>
    </div>
    <button class="try-btn" onclick="tryApi('/api/mission_queue', 'res-mq')">&#9654; Try it live</button>
    <div class="response-live" id="res-mq"><pre id="res-mq-data">Loading...</pre></div>
  </div>

  <div class="endpoint">
    <div class="endpoint-header">
      <span class="method get">GET</span>
      <span class="endpoint-path">/api/sgp4</span>
      <span class="tag tag-live">REAL-TIME</span>
    </div>
    <div class="endpoint-desc">Returns real-time SGP4-propagated positions for all debris objects. Includes latitude, longitude, altitude, and velocity computed using the same algorithm used by NASA and NORAD.</div>
    <div class="response-box">
      <pre>[
  {
    "name": "DELTA 1 DEB",
    "lat": 23.4,
    "lon": 142.1,
    "alt_km": 843.2,
    "velocity_km_s": 7.4
  }, ...
]</pre>
    </div>
    <button class="try-btn" onclick="tryApi('/api/sgp4', 'res-sgp4')">&#9654; Try it live</button>
    <div class="response-live" id="res-sgp4"><pre id="res-sgp4-data">Loading...</pre></div>
  </div>

</div>

<script>
async function tryApi(endpoint, divId) {
  const div = document.getElementById(divId);
  const pre = document.getElementById(divId + '-data');
  div.style.display = 'block';
  pre.textContent = 'Fetching...';
  try {
    const res = await fetch(endpoint);
    const data = await res.json();
    pre.textContent = JSON.stringify(data, null, 2).substring(0, 2000) + (JSON.stringify(data).length > 2000 ? '\\n... (truncated)' : '');
  } catch(e) {
    pre.textContent = 'Error: ' + e.message;
  }
}
</script>
</body>
</html>
''')
print("api_docs.html created successfully!")