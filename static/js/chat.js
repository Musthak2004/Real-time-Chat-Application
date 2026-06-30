(function() {
  var conversationId = window.CONVERSATION_ID;
  var username = window.USERNAME;
  if (!conversationId) return;

  var wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
  var wsUrl = wsScheme + '://' + window.location.host + '/ws/chat/' + conversationId + '/';
  var ws = null;
  var reconnectTimer = null;

  function connectWebSocket() {
    ws = new WebSocket(wsUrl);

    ws.onmessage = function(e) {
      var data = JSON.parse(e.data);
      if (data.sender_id === undefined) return;

      var container = document.querySelector('.chat-messages');
      var empty = container.querySelector('.empty');
      if (empty) empty.remove();

      var div = document.createElement('div');
      div.className = 'message' + (data.sender_username === username ? ' sent' : ' received');

      if (data.sender_username !== username) {
        var sender = document.createElement('div');
        sender.className = 'msg-sender';
        sender.textContent = data.sender_username;
        div.appendChild(sender);
      }
      var body = document.createElement('div');
      body.textContent = data.content;
      div.appendChild(body);
      var time = document.createElement('div');
      time.className = 'msg-time';
      time.textContent = new Date(data.created_at).toLocaleTimeString([], {hour:'numeric', minute:'2-digit'});
      div.appendChild(time);

      container.appendChild(div);
      container.scrollTop = container.scrollHeight;
    };

    ws.onclose = function() {
      if (reconnectTimer) return;
      reconnectTimer = setTimeout(function() {
        reconnectTimer = null;
        connectWebSocket();
      }, 3000);
    };
  }

  connectWebSocket();

  document.getElementById('chat-form').addEventListener('submit', function(e) {
    var input = document.getElementById('chat-input');
    var content = input.value.trim();
    if (!content) { e.preventDefault(); return; }

    if (ws.readyState === WebSocket.OPEN) {
      e.preventDefault();
      ws.send(JSON.stringify({ content: content }));
      input.value = '';
    }
  });
})();
