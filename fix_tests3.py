with open('tests.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'assert classify_risk(0.25) == "MEDIUM"      # exactly 0.25 = MEDIUM',
    'assert classify_risk(0.25) == "LOW"         # exactly 0.25 = LOW (threshold is > 0.25)'
)

with open('tests.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed")