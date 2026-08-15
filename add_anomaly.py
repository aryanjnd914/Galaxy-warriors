panel = '''
<!-- ANOMALY DETECTION PANEL -->
<div style="margin: 0 24px 24px;">
  <div style="background:#0a0a1a;border:1px solid #ff440033;border-radius:12px;padding:20px;">
    <div style="color:#ff4444;font-size:11px;letter-spacing:2px;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
      <span style="width:3px;height:12px;background:#ff4444;border-radius:2px;display:inline-block;"></span>
      ANOMALY DETECTION — ISOLATION FOREST ML MODEL
    </div>
    <div id="anomaly-loading" style="color:#555;font-size:12px;">Scanning for anomalies...</div>
    <div id="anomaly-content" style="display:none;">
      <div id="anomaly-summary" style="margin-bottom:12px;font-size:12px;color:#888;"></div>
      <table style="width:100%;border-collapse:collapse;font-size:12px;">
        <thead>
          <tr>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">OBJECT</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">STATUS</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">ANOMALY SCORE</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">PERIGEE</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">ECCENTRICITY</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">DRAG (BSTAR)</th>
          </tr>
        </thead>
        <tbody id="anomaly-body"></tbody>
      </table>
    </div>
  </div>
</div>

<script>
async function loadAnomalies() {
  try {
    const res = await fetch('/api/anomalies');
    const data = await res.json();
    document.getElementById('anomaly-loading').style.display = 'none';
    document.getElementById('anomaly-content').style.display = 'block';

    const anomalies = data.filter(d => d.is_anomaly);
    document.getElementById('anomaly-summary').innerHTML =
      `Isolation Forest scanned <b style="color:#fff">${data.length}</b> objects — 
       <b style="color:#ff4444">${anomalies.length} anomalies</b> detected with unusual orbital decay patterns.`;

    document.getElementById('anomaly-body').innerHTML = data.map(d => {
      const isAnom = d.is_anomaly;
      const rowBg = isAnom ? 'background:#1a0505;' : '';
      const statusColor = isAnom ? '#ff4444' : '#00cc44';
      const scoreColor = d.anomaly_score > 60 ? '#ff4444' : d.anomaly_score > 30 ? '#ff8800' : '#00cc44';
      return `<tr style="${rowBg}">
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:#fff;font-weight:${isAnom?'bold':'normal'}">${d.name}</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;">
          <span style="color:${statusColor};font-weight:bold;font-size:11px;">${d.anomaly_label}</span>
        </td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;">
          <span style="color:${scoreColor};font-weight:bold;">${d.anomaly_score}%</span>
          <span style="display:inline-block;width:60px;height:4px;background:#1a1a2e;border-radius:2px;margin-left:8px;vertical-align:middle;">
            <span style="display:block;width:${d.anomaly_score}%;height:4px;background:${scoreColor};border-radius:2px;"></span>
          </span>
        </td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:#aaa;">${d.perigee} km</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:#aaa;">${d.eccentricity}</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:#aaa;">${d.bstar}</td>
      </tr>`;
    }).join('');
  } catch(e) {
    document.getElementById('anomaly-loading').textContent = 'Error loading anomaly data.';
  }
}
loadAnomalies();
</script>
'''

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert before Monte Carlo panel
content = content.replace('<!-- MONTE CARLO PANEL -->', panel + '\n<!-- MONTE CARLO PANEL -->')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Anomaly panel added successfully")