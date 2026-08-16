import re

with open("templates/simulation.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add livepulse animation to CSS
old_css = "  @keyframes kpulse { 0%,100%{box-shadow:0 0 4px #ff000066} 50%{box-shadow:0 0 14px #ff0000cc,0 0 28px #ff000044} }"
new_css = old_css + "\n  @keyframes livepulse { 0%,100%{opacity:1;box-shadow:0 0 6px #00ff88} 50%{opacity:0.4;box-shadow:0 0 2px #00ff88} }"
html = html.replace(old_css, new_css)

# 2. Add live badge to topbar
old_topbar = '  <div style="display:flex;align-items:center">\n    <div class="logo">ORBIT<span>-</span>GUARD</div>\n    <span class="subtitle">3D ORBITAL SIMULATION</span>\n  </div>'
new_topbar = '''  <div style="display:flex;align-items:center;gap:20px">
    <div class="logo">ORBIT<span>-</span>GUARD</div>
    <span class="subtitle">3D ORBITAL SIMULATION</span>
    <div id="live-badge" style="display:flex;align-items:center;gap:8px;background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.2);border-radius:20px;padding:4px 14px;font-size:10px;letter-spacing:1.5px;color:#00ff88;font-family:'Courier New',monospace;transition:all 0.5s;">
      <span id="live-dot" style="width:7px;height:7px;border-radius:50%;background:#00ff88;display:inline-block;box-shadow:0 0 6px #00ff88;animation:livepulse 2s infinite;flex-shrink:0;"></span>
      <span id="live-label">LIVE</span>
      <span style="color:#1a3a2a;margin:0 4px">|</span>
      <span style="color:#336644;font-size:9px">UPDATED</span>&nbsp;<span id="live-update" style="color:#00ff88">--:--</span>
      <span style="color:#1a3a2a;margin:0 4px">|</span>
      <span style="color:#336644;font-size:9px">NEXT</span>&nbsp;<span id="live-next" style="color:#00ff88;font-weight:bold">--:--</span>
    </div>
  </div>'''
html = html.replace(old_topbar, new_topbar)

# 3. Add scheduler JS before closing </script></body></html>
badge_js = '''
// Live Scheduler Badge
async function updateLiveBadge() {
  try {
    const res = await fetch('/api/scheduler_status');
    const s = await res.json();
    const badge = document.getElementById('live-badge');
    const dot = document.getElementById('live-dot');
    const label = document.getElementById('live-label');
    const update = document.getElementById('live-update');
    const next = document.getElementById('live-next');
    if(s.running) {
      badge.style.borderColor = 'rgba(0,255,136,0.4)';
      badge.style.background = 'rgba(0,255,136,0.08)';
      dot.style.background = '#00ff88';
      dot.style.boxShadow = '0 0 8px #00ff88';
      label.textContent = s.update_count > 0 ? 'LIVE x'+s.update_count : 'LIVE';
      label.style.color = '#00ff88';
      if(s.last_update && s.last_update !== 'Never') {
        const p = s.last_update.split(' ');
        update.textContent = (p[1]||'--:--').slice(0,5)+' UTC';
      } else { update.textContent = 'STARTUP'; }
      if(s.next_update && s.next_update !== 'N/A') {
        const p = s.next_update.split(' ');
        next.textContent = (p[0]||'--:--').slice(0,5);
      } else { next.textContent = '60:00'; }
    } else {
      badge.style.borderColor='rgba(255,68,68,0.3)';
      badge.style.background='rgba(255,68,68,0.05)';
      dot.style.background='#ff4444'; dot.style.boxShadow='0 0 6px #ff4444';
      label.textContent='OFFLINE'; label.style.color='#ff4444';
      update.textContent='--:--'; next.textContent='--:--';
    }
  } catch(e) {
    const label=document.getElementById('live-label');
    const dot=document.getElementById('live-dot');
    if(label){label.textContent='LOCAL';label.style.color='#ffcc00';}
    if(dot){dot.style.background='#ffcc00';dot.style.boxShadow='0 0 6px #ffcc00';}
  }
}
updateLiveBadge();
setInterval(updateLiveBadge, 30000);
'''

html = html.replace('</script>\n</body>\n</html>', badge_js + '</script>\n</body>\n</html>')

with open("templates/simulation.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Done - live badge added to simulation.html")
