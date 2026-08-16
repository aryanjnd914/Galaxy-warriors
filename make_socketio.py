# Minimal Socket.IO client compatible with flask-socketio
content = r"""
(function(global){
  var callbacks = {};
  var ws = null;
  var connected = false;

  function connect() {
    var wsUrl = 'ws://' + window.location.host + '/socket.io/?transport=websocket&EIO=4';
    try {
      ws = new WebSocket(wsUrl);
    } catch(e) {
      setTimeout(connect, 3000);
      return;
    }

    ws.onopen = function() {
      ws.send('40');
    };

    ws.onmessage = function(e) {
      var data = e.data;
      if (data === '2') { ws.send('3'); return; }
      if (data.startsWith('40')) {
        connected = true;
        if (callbacks['connect']) callbacks['connect'].forEach(function(fn){ fn(); });
        return;
      }
      if (data.startsWith('42')) {
        try {
          var payload = JSON.parse(data.slice(2));
          var event = payload[0];
          var edata = payload[1];
          if (callbacks[event]) callbacks[event].forEach(function(fn){ fn(edata); });
        } catch(err) {}
      }
    };

    ws.onclose = function() {
      connected = false;
      if (callbacks['disconnect']) callbacks['disconnect'].forEach(function(fn){ fn(); });
      setTimeout(connect, 3000);
    };

    ws.onerror = function() {
      ws.close();
    };
  }

  function io() {
    connect();
    return {
      on: function(event, fn) {
        if (!callbacks[event]) callbacks[event] = [];
        callbacks[event].push(fn);
      },
      emit: function(event, data) {
        if (ws && ws.readyState === 1) {
          ws.send('42' + JSON.stringify([event, data]));
        }
      },
      connected: function() { return connected; }
    };
  }

  global.io = io;
})(window);
"""

with open('static/socket.io.min.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Socket.IO client created successfully")