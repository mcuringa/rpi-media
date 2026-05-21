const WebSocket = require("ws");

function setupWebsocket(server) {
    const wss = new WebSocket.Server({ server });

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