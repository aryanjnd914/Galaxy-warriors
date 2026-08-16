with open('templates/simulation.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''  const angle = (lon / 360) * Math.PI * 2;
  const latRad = (lat / 180) * Math.PI;
  const issOrbitR = EARTH_R + 20 + Math.cos(latRad) * 10;

  const ix = CX + Math.cos(angle) * issOrbitR;
  const iy = CY + Math.sin(angle) * issOrbitR * 0.6; // slight ellipse for perspective'''

new = '''  // ISS orbits at ~408km — map to screen radius between debris orbits
  const issOrbitR = EARTH_R + 60;
  const angle = (lon / 180) * Math.PI; // full rotation mapped to canvas
  const latOffset = (lat / 90) * 20;   // latitude shifts up/down

  const ix = CX + Math.cos(angle) * issOrbitR;
  const iy = CY + Math.sin(angle) * issOrbitR + latOffset;'''

content = content.replace(old, new)

with open('templates/simulation.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("ISS positioning fixed")