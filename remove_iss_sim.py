with open('templates/simulation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove ISS panel HTML
import re
content = re.sub(r'<!-- ISS INFO BAR -->.*?</div>\s*<!-- ISS PROXIMITY WARNING -->.*?</div>', '', content, flags=re.DOTALL)

# Remove ISS JS
content = re.sub(r'// ─── ISS LIVE POSITION ────.*?setInterval\(loadISS, 5000\);', '', content, flags=re.DOTALL)

# Remove drawISS() call
content = content.replace('drawMission(); drawISS(); drawStats();', 'drawMission(); drawStats();')

with open('templates/simulation.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("ISS removed from simulation")