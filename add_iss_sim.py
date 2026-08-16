iss_code = '''
// ─── ISS LIVE POSITION ────────────────────────────────────────────────────
let issPosition = null;
let issWarning = false;

async function loadISS() {
  try {
    const res = await fetch('/api/iss');
    issPosition = await res.json();
    updateISSDisplay();
  } catch(e) {
    console.log('ISS fetch failed:', e);
  }
}

function updateISSDisplay() {
  const el = document.getElementById('iss-info');
  if (el && issPosition) {
    el.innerHTML = `
      <span style="color:#00ff88;font-weight:bold;">&#9650; ISS</span>
      LAT: ${parseFloat(issPosition.latitude).toFixed(2)}°
      LON: ${parseFloat(issPosition.longitude).toFixed(2)}°
      ALT: ${issPosition.altitude_km} km
    `;
  }
}

function drawISS() {
  if (!issPosition) return;

  // Convert lat/lon to canvas position (simple equirectangular)
  const lat = parseFloat(issPosition.latitude);
  const lon = parseFloat(issPosition.longitude);

  // Map lat/lon to orbit around Earth center
  const angle = (lon / 360) * Math.PI * 2;
  const latRad = (lat / 180) * Math.PI;
  const issOrbitR = EARTH_R + 20 + Math.cos(latRad) * 10;

  const ix = CX + Math.cos(angle) * issOrbitR;
  const iy = CY + Math.sin(angle) * issOrbitR * 0.6; // slight ellipse for perspective

  // ISS glow
  ctx.save();
  ctx.globalAlpha = 0.3 + 0.2 * Math.sin(Date.now() * 0.003);
  ctx.fillStyle = '#00ff88';
  ctx.beginPath();
  ctx.arc(ix, iy, 12, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // ISS dot
  ctx.fillStyle = '#00ff88';
  ctx.beginPath();
  ctx.arc(ix, iy, 6, 0, Math.PI * 2);
  ctx.fill();

  // ISS label
  ctx.fillStyle = '#00ff88';
  ctx.font = 'bold 10px Courier New';
  ctx.fillText('ISS', ix + 10, iy - 6);
  ctx.font = '9px Courier New';
  ctx.fillStyle = '#008844';
  ctx.fillText(`${parseFloat(issPosition.latitude).toFixed(1)}° ${parseFloat(issPosition.longitude).toFixed(1)}°`, ix + 10, iy + 6);

  // Check proximity to debris — warn if any debris within 150px
  issWarning = false;
  debris.forEach(d => {
    if (!d.x || removedIds.has(d.norad_id)) return;
    const dist = Math.sqrt((ix - d.x) ** 2 + (iy - d.y) ** 2);
    if (dist < 150) {
      issWarning = true;
      // Draw warning line
      ctx.save();
      ctx.strokeStyle = '#ff4444';
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.4 + 0.3 * Math.sin(Date.now() * 0.01);
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(ix, iy);
      ctx.lineTo(d.x, d.y);
      ctx.stroke();
      ctx.restore();

      // Warning label
      ctx.fillStyle = '#ff4444';
      ctx.font = 'bold 9px Courier New';
      ctx.fillText('⚠ PROXIMITY ALERT', ix + 10, iy + 20);
    }
  });

  // ISS warning banner
  const banner = document.getElementById('iss-warning');
  if (banner) {
    banner.style.display = issWarning ? 'block' : 'none';
  }

  issPosition._ix = ix;
  issPosition._iy = iy;
}

// Refresh ISS position every 5 seconds
loadISS();
setInterval(loadISS, 5000);
'''

# ISS panel HTML to add to topbar controls
iss_panel = '''
  <!-- ISS INFO BAR -->
  <div style="position:fixed;bottom:40px;left:20px;background:#0d0d1acc;border:1px solid #00ff8833;border-radius:8px;padding:8px 14px;font-family:monospace;font-size:11px;z-index:999;">
    <span style="color:#00ff88;letter-spacing:1px;">&#9650; ISS LIVE</span>
    <span id="iss-info" style="color:#555;margin-left:10px;">Loading...</span>
  </div>

  <!-- ISS PROXIMITY WARNING -->
  <div id="iss-warning" style="display:none;position:fixed;top:60px;left:50%;transform:translateX(-50%);background:#ff000033;border:1px solid #ff4444;border-radius:8px;padding:10px 24px;font-family:monospace;font-size:12px;color:#ff4444;letter-spacing:2px;z-index:9999;animation:alertpulse 1s infinite;">
    ⚠ ISS PROXIMITY ALERT — DEBRIS CONJUNCTION RISK
  </div>
'''

with open('templates/simulation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add ISS panel HTML before </body>
if 'iss-info' not in content:
    content = content.replace('</body>', iss_panel + '\n</body>')
    print("ISS panel HTML added")

# Add ISS JS before </script> closing of main animate script
if 'drawISS' not in content:
    content = content.replace(
        'loadDebris().then(animate);',
        iss_code + '\nloadDebris().then(animate);'
    )
    print("ISS JavaScript added")

# Add drawISS() call inside animate function
if 'drawISS()' not in content:
    content = content.replace(
        'drawMission(); drawStats();',
        'drawMission(); drawISS(); drawStats();'
    )
    print("drawISS() added to animation loop")

with open('templates/simulation.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("ISS overlay added to simulation successfully")