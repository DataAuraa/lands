type MessageHandler = (data: any) => void;

class WebSocketClient {
  private sockets: Map<string, WebSocket> = new Map();
  private handlers: Map<string, Set<MessageHandler>> = new Map();

  connect(channel: 'dashboard' | 'alerts' | 'sensors') {
    if (this.sockets.has(channel)) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/${channel}`;

    try {
      const ws = new WebSocket(wsUrl);
      this.sockets.set(channel, ws);

      ws.onopen = () => {
        // Connected
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const channelHandlers = this.handlers.get(channel);
          if (channelHandlers) {
            channelHandlers.forEach((handler) => handler(data));
          }
        } catch {
          // ignore non-json
        }
      };

      ws.onclose = () => {
        this.sockets.delete(channel);
        // Retry connection after 5 seconds
        setTimeout(() => this.connect(channel), 5000);
      };
    } catch {
      // Offline fallback
    }
  }

  subscribe(channel: 'dashboard' | 'alerts' | 'sensors', handler: MessageHandler) {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
    }
    this.handlers.get(channel)!.add(handler);
    this.connect(channel);

    return () => {
      this.handlers.get(channel)?.delete(handler);
    };
  }
}

export const wsClient = new WebSocketClient();
