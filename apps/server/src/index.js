const createApp = require("./app");

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || "0.0.0.0";
const { server, mediaRoot, kioskRoot } = createApp();

server.listen(PORT, HOST, () => {
    console.log(`server listening on ${HOST}:${PORT}`);
    console.log(`serving media from ${mediaRoot}`);
    console.log(`serving kiosk from ${kioskRoot}`);
});
