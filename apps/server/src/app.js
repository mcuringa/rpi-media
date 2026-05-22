const express = require("express");
const cors = require("cors");
const http = require("http");
const path = require("path");

const setupWebsocket = require("./socket");
const createApiRouter = require("./api/routes");

function createApp(options = {}) {
    const app = express();
    const mediaRoot = options.mediaRoot || process.env.MEDIA_ROOT || path.join(__dirname, "..", "..", "kiosk", "media");
    const kioskRoot = options.kioskRoot || process.env.KIOSK_ROOT || path.join(__dirname, "..", "..", "kiosk", "dist");

    app.use(cors());
    app.use(express.json());
    app.use("/media", express.static(mediaRoot));

    app.get("/health", (req, res) => {
        res.json({ ok: true });
    });

    const server = http.createServer(app);
    const wss = setupWebsocket(server);

    app.locals.wss = wss;
    app.locals.mediaRoot = mediaRoot;
    app.locals.kioskRoot = kioskRoot;
    app.use("/api", createApiRouter());
    app.use(express.static(kioskRoot));

    app.get(/^\/(?!api\/|media\/|health$).*/, (req, res) => {
        res.sendFile(path.join(kioskRoot, "index.html"));
    });

    return { app, server, wss, mediaRoot, kioskRoot };
}

module.exports = createApp;
