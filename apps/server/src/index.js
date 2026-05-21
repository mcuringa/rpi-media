const express = require("express");
const cors = require("cors");
const http = require("http");

const setupWebsocket = require("./socket");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get("/health", (req, res) => {
    res.json({ ok: true });
});

const server = http.createServer(app);

setupWebsocket(server);

server.listen(PORT, () => {
    console.log(`server listening on ${PORT}`);
});