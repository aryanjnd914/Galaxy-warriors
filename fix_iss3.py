with open('templates/simulation.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''async function loadISS() {
  try {
    const res = await fetch('/api/iss');
    issPosition = await res.json();
    updateISSDisplay();
  } catch(e) {
    console.log('ISS fetch failed:', e);
  }
}'''

new = '''async function loadISS() {
  try {
    const res = await fetch('/api/iss');
    issPosition = await res.json();
    console.log('[ISS] Position:', issPosition);
    const el = document.getElementById('iss-info');
    if (el) {
      el.innerHTML = `LAT: ${parseFloat(issPosition.latitude).toFixed(2)}&deg; LON: ${parseFloat(issPosition.longitude).toFixed(2)}&deg; ALT: ${issPosition.altitude_km} km`;
      el.style.color = '#00ff88';
    }
  } catch(e) {
    console.log('[ISS] fetch failed:', e);
    const el = document.getElementById('iss-info');
    if (el) el.innerHTML = 'API ERROR';
  }
}'''

content = content.replace(old, new)

with open('templates/simulation.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("ISS display fix applied")