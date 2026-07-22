const express = require("express");

const mediaKinds = new Map([
    ["img", "image"],
    ["video", "video"],
    ["audio", "audio"]
]);
const displayMediaPathPattern = /^\/(img|video)\/d(\d+)\/(.+)$/;
const audioMediaPathPattern = /^\/audio\/(.+)$/;
const clearDisplayPathPattern = /^\/clear\/d(\d+)$/;

function cleanMediaPath(value) {
    return value
        .split("/")
        .filter((segment) => segment && segment !== "." && segment !== "..")
        .join("/");
}

function createMediaEvent({ kind, display, mediaPath }) {
    const mediaType = mediaKinds.get(kind);
    const safePath = cleanMediaPath(mediaPath);

    if (!mediaType || !safePath) {
        return null;
    }

    return {
        type: "media",
        kind,
        mediaType,
        display,
        filename: safePath,
        createdAt: new Date().toISOString()
    };
}

function sendMediaEvent(req, res, event) {
    req.app.locals.wss.broadcastJson(event);
    res.json({
        ok: true,
        event,
        listeners: req.app.locals.wss.clients.size
    });
}

module.exports = function createApiRouter() {
    const router = express.Router();

    router.all(clearDisplayPathPattern, (req, res) => {
        const [, display] = req.path.match(clearDisplayPathPattern);
        const event = {
            type: "clear",
            display: Number(display),
            createdAt: new Date().toISOString()
        };

        sendMediaEvent(req, res, event);
    });

    router.all(displayMediaPathPattern, (req, res) => {
        const [, kind, display, mediaPath] = req.path.match(displayMediaPathPattern);
        const event = createMediaEvent({
            kind,
            display: Number(display),
            mediaPath
        });

        if (!event) {
            res.status(400).json({ ok: false, error: "Invalid media trigger path." });
            return;
        }

        sendMediaEvent(req, res, event);
    });

    router.all(audioMediaPathPattern, (req, res) => {
        const [, mediaPath] = req.path.match(audioMediaPathPattern);
        const event = createMediaEvent({
            kind: "audio",
            display: null,
            mediaPath
        });

        if (!event) {
            res.status(400).json({ ok: false, error: "Invalid audio trigger path." });
            return;
        }

        sendMediaEvent(req, res, event);
    });

    return router;
};
