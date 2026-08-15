panel = '''
<!-- DECAY PREDICTION PANEL -->
<div style="margin: 0 24px 24px;">
  <div style="background:#0a0a1a;border:1px solid #00ff8833;border-radius:12px;padding:20px;">
    <div style="color:#00ff88;font-size:11px;letter-spacing:2px;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
      <span style="width:3px;height:12px;background:#00ff88;border-radius:2px;display:inline-block;"></span>
      30-DAY ORBITAL DECAY PREDICTION — LINEAR REGRESSION MODEL
    </div>
    <div id="pred-loading" style="color:#555;font-size:12px;">Computing decay predictions...</div>
    <div id="pred-content" style="display:none;">
      <div id="pred-summary" style="margin-bottom:12px;font-size:12px;color:#888;"></div>
      <table style="width:100%;border-collapse:collapse;font-size:12px;">
        <thead>
          <tr>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">OBJECT</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">CURRENT ALT</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">PREDICTED (30D)</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">TOTAL DECAY</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">DAILY RATE</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">TREND</th>
            <th style="color:#444;font-weight:normal;padding:8px 10px;text-align:left;border-bottom:1px solid #1a1a3a;letter-spacing:1px;font-size:10px;">REENTRY</th>
          </tr>
        </thead>
        <tbody id="pred-body"></tbody>
      </table>
    </div>
  </div>
</div>

<script>
async function loadPredictions() {
  try {
    const res = await fetch('/api/predictions');
    const data = await res.json();
    document.getElementById('pred-loading').style.display = 'none';
    document.getElementById('pred-content').style.display = 'block';
    const rapid = data.filter(d => d.trend === 'RAPID DECAY').length;
    const reentry = data.filter(d => d.reentry_day !== null).length;
    document.getElementById('pred-summary').innerHTML =
      `Linear regression model predicts <b style="color:#ff4444">${rapid} objects</b> in rapid decay —
       <b style="color:#ff4444">${reentry} objects</b> predicted to reenter within 30 days.`;
    document.getElementById('pred-body').innerHTML = data.map(d => {
      const reentryText = d.reentry_day !== null
        ? `<span style="color:#ff4444;font-weight:bold;">DAY ${d.reentry_day}</span>`
        : '<span style="color:#444;">STABLE</span>';
      return `<tr>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:#fff;font-weight:bold;">${d.name}</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:#aaa;">${d.current_perigee} km</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:#00d4ff;">${d.predicted_30d} km</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:${d.trend_color};">-${d.total_decay_km} km</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:#aaa;">${d.daily_decay_km} km/day</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;color:${d.trend_color};font-weight:bold;">${d.trend}</td>
        <td style="padding:9px 10px;border-bottom:1px solid #0d0d1a;">${reentryText}</td>
      </tr>`;
    }).join('');
  } catch(e) {
    document.getElementById('pred-loading').textContent = 'Error loading predictions.';
  }
}
loadPredictions();
</script>
'''

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert before closing body tag
content = content.replace('</body>', panel + '\n</body>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Decay prediction panel added successfully")