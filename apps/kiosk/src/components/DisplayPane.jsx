import React from "react";

import MediaPlayer from "./MediaPlayer";

export default function DisplayPane({ visualMedia, audioMedia, onVideoEnded }) {
    return (
        <main className="kiosk-stage">
            <MediaPlayer media={visualMedia} onVideoEnded={onVideoEnded} />
            <MediaPlayer media={audioMedia} />
        </main>
    );
}
