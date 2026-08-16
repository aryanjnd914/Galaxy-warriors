with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'https://cdn.socket.io/4.7.2/socket.io.min.js',
    '/static/socket.io.min.js'
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")