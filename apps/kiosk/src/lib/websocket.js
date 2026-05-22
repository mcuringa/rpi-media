const DEFAULT_SERVER_PORT = "3000";

function isViteDevServer(location) {
    return location.port && location.port !== DEFAULT_SERVER_PORT;
}

export function getServerOrigin() {
    if (import.meta.env.VITE_MEDIA_BASE_URL) {
        return import.meta.env.VITE_MEDIA_BASE_URL.replace(/\/$/, "");
    }

    if (isViteDevServer(window.location)) {
        return `${window.location.protocol}//${window.location.hostname}:${DEFAULT_SERVER_PORT}`;
    }

    return window.location.origin;
}

export function getWebsocketUrl() {
    if (import.meta.env.VITE_WS_URL) {
        return import.meta.env.VITE_WS_URL;
    }

    const serverOrigin = new URL(getServerOrigin());
    serverOrigin.protocol = serverOrigin.protocol === "https:" ? "wss:" : "ws:";
    return serverOrigin.toString();
}

export function resolveServerPath(path) {
    if (/^https?:\/\//.test(path)) {
        return path;
    }

    return `${getServerOrigin()}${path.startsWith("/") ? path : `/${path}`}`;
}

export function resolveMediaSrc(mediaType, filename) {
    const mediaFolders = {
        image: "img",
        video: "video",
        audio: "audio"
    };
    const mediaFolder = mediaFolders[mediaType];

    if (!mediaFolder || !filename) {
        return "";
    }

    if (/^\/?media\//.test(filename) || /^https?:\/\//.test(filename)) {
        return resolveServerPath(filename);
    }

    return resolveServerPath(`/media/${mediaFolder}/${filename}`);
}

export function connectMediaSocket({ onMessage, onStatus }) {
    let socket;
    let reconnectTimer;
    let shouldReconnect = true;

    const connect = () => {
        socket = new WebSocket(getWebsocketUrl());

        socket.addEventListener("open", () => onStatus?.("connected"));
        socket.addEventListener("close", () => {
            onStatus?.("disconnected");

            if (shouldReconnect) {
                reconnectTimer = window.setTimeout(connect, 1000);
            }
        });
        socket.addEventListener("error", () => onStatus?.("error"));
        socket.addEventListener("message", (message) => {
            try {
                onMessage?.(JSON.parse(message.data));
            } catch (error) {
                console.warn("Ignoring malformed websocket message", error);
            }
        });
    };

    connect();

    return () => {
        shouldReconnect = false;
        window.clearTimeout(reconnectTimer);
        socket?.close();
    };
}
