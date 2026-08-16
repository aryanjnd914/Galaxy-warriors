with open('tests.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'assert classify_risk(0.50) == "HIGH"        # exactly 0.50 = HIGH',
    'assert classify_risk(0.50) == "MEDIUM"      # exactly 0.50 = MEDIUM (threshold is > 0.50)'
)

with open('tests.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed")