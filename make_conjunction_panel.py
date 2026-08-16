with open("templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

socketio_js = """
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
const socket = io();

socket.on('connect', function() {
    console.log('[ORBIT-GUARD] WebSocket connected — live updates active');
    document.getElementById('ws-status').textContent = 'LIVE';
    document.getElementById('ws-status').style.color = '#00ff88';
});

socket.on('disconnect', function() {
    document.getElementById('ws-status').textContent = 'OFFLINE';
    document.getElementById('ws-status').style.color = '#ff003c';
});

socket.on('live_update', function(data) {
    // Update timestamp
    document.getElementById('ws-timestamp').textContent = data.timestamp;

    // Update SGP4 positions if displayed
    if (data.sgp4 && window.updateSGP4) {
        window.updateSGP4(data.sgp4);
    }

    // Flash the live indicator
    const indicator = document.getElementById('ws-status');
    indicator.style.color = '#ffffff';
    setTimeout(() => { indicator.style.color = '#00ff88'; }, 200);

    console.log('[ORBIT-GUARD] Live update received:', data.timestamp);
});
</script>
"""

# Add WebSocket status indicator to page
ws_indicator = """
<div style="position:fixed;bottom:16px;right:16px;background:#0d0d1a;border:1px solid #333;border-radius:8px;padding:8px 14px;font-family:monospace;font-size:0.75rem;z-index:9999;">
  <span style="color:#888;">WS</span>
  <span id="ws-status" style="color:#ff003c;margin-left:6px;font-weight:bold;">CONNECTING...</span>
  <span id="ws-timestamp" style="color:#555;margin-left:10px;">--:--:--</span>
</div>
"""

if "</body>" in content:
    content = content.replace("</body>", ws_indicator + socketio_js + "</body>")
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("WebSocket client added to dashboard!")
else:
    print("ERROR: Could not find </body>")