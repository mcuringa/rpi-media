const WebSocket = require("ws");

function broadcastJson(wss, payload) {
    const message = JSON.stringify(payload);

    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

function setupWebsocket(server) {
    const wss = new WebSocket.Server({ server });

    wss.broadcastJson = (payload) => broadcastJson(wss, payload);

    wss.on("connection", (ws) => {
        console.log("client connected");

        ws.send(JSON.stringify({
            type: "hello",
            message: "connected"
        }));

        ws.on("close", () => {
            console.log("client disconnected");
        });
    });

    return wss;
}

module.exports = setupWebsocket;
