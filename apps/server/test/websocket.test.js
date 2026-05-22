const assert = require("node:assert/strict");
const http = require("node:http");
const { afterEach, test } = require("node:test");
const WebSocket = require("ws");

const createApp = require("../src/app");

const openServers = [];
const openSockets = [];

function listen(server) {
    return new Promise((resolve, reject) => {
        server.once("error", reject);
        server.listen(0, "127.0.0.1", () => {
            server.off("error", reject);
            resolve(server.address().port);
        });
    });
}

function closeServer(server) {
    return new Promise((resolve, reject) => {
        server.close((error) => {
            if (error) {
                reject(error);
                return;
            }

            resolve();
        });
    });
}

function waitForSocketOpen(socket) {
    return new Promise((resolve, reject) => {
        socket.once("open", resolve);
        socket.once("error", reject);
    });
}

function waitForMessage(socket, predicate, timeoutMs = 1000) {
    return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
            socket.off("message", onMessage);
            reject(new Error("Timed out waiting for websocket message."));
        }, timeoutMs);

        function onMessage(data) {
            const message = JSON.parse(data.toString());

            if (!predicate(message)) {
                return;
            }

            clearTimeout(timeout);
            socket.off("message", onMessage);
            resolve(message);
        }

        socket.on("message", onMessage);
    });
}

async function getJson(url) {
    return new Promise((resolve, reject) => {
        const request = http.get(url, (response) => {
            let body = "";

            response.setEncoding("utf8");
            response.on("data", (chunk) => {
                body += chunk;
            });
            response.on("end", () => {
                if (response.statusCode < 200 || response.statusCode >= 300) {
                    reject(new Error(`Expected 2xx response, got ${response.statusCode}: ${body}`));
                    return;
                }

                resolve(JSON.parse(body));
            });
        });

        request.setTimeout(1000, () => {
            request.destroy(new Error(`Timed out waiting for HTTP response from ${url}`));
        });
        request.on("error", reject);
    });
}

afterEach(async () => {
    while (openSockets.length) {
        const socket = openSockets.pop();

        if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
            socket.close();
        }
    }

    while (openServers.length) {
        await closeServer(openServers.pop());
    }
});

test("websocket clients receive a hello message on connect", async () => {
    const { server } = createApp();
    openServers.push(server);

    const port = await listen(server);
    const socket = new WebSocket(`ws://127.0.0.1:${port}`);
    openSockets.push(socket);

    const helloMessage = waitForMessage(socket, (message) => message.type === "hello");
    await waitForSocketOpen(socket);

    assert.deepEqual(await helloMessage, {
        type: "hello",
        message: "connected"
    });
});

test("image REST triggers broadcast a media event to websocket clients", async () => {
    const { server } = createApp();
    openServers.push(server);

    const port = await listen(server);
    const socket = new WebSocket(`ws://127.0.0.1:${port}`);
    openSockets.push(socket);

    const helloMessage = waitForMessage(socket, (message) => message.type === "hello");
    await waitForSocketOpen(socket);
    await helloMessage;

    const mediaMessage = waitForMessage(socket, (message) => message.type === "media");
    const response = await getJson(`http://127.0.0.1:${port}/api/img/d1/battle-of-brooklyn-1776.jpg`);

    assert.equal(response.ok, true);
    assert.equal(response.listeners, 1);
    assert.match(response.event.createdAt, /^\d{4}-\d{2}-\d{2}T/);
    assert.deepEqual(
        {
            ...response.event,
            createdAt: "<timestamp>"
        },
        {
            type: "media",
            kind: "img",
            mediaType: "image",
            display: 1,
            filename: "battle-of-brooklyn-1776.jpg",
            createdAt: "<timestamp>"
        }
    );

    const broadcast = await mediaMessage;
    assert.deepEqual(broadcast, response.event);
});

test("audio REST triggers broadcast display-independent audio events", async () => {
    const { server } = createApp();
    openServers.push(server);

    const port = await listen(server);
    const socket = new WebSocket(`ws://127.0.0.1:${port}`);
    openSockets.push(socket);

    const helloMessage = waitForMessage(socket, (message) => message.type === "hello");
    await waitForSocketOpen(socket);
    await helloMessage;

    const mediaMessage = waitForMessage(socket, (message) => message.type === "media");
    const response = await getJson(`http://127.0.0.1:${port}/api/audio/old-town.mp3`);

    assert.equal(response.ok, true);
    assert.equal(response.event.kind, "audio");
    assert.equal(response.event.mediaType, "audio");
    assert.equal(response.event.display, null);
    assert.equal(response.event.filename, "old-town.mp3");
    assert.deepEqual(await mediaMessage, response.event);
});
