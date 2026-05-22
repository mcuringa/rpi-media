const createApp = require("./app");

const PORT = process.env.PORT || 3000;
const { server, mediaRoot, kioskRoot } = createApp();

server.listen(PORT, () => {
    console.log(`server listening on ${PORT}`);
    console.log(`serving media from ${mediaRoot}`);
    console.log(`serving kiosk from ${kioskRoot}`);
});
