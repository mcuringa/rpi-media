import React, { useEffect, useMemo, useState } from "react";

import DisplayPane from "./components/DisplayPane";
import { getMediaType, isMediaEvent, MEDIA_TYPES } from "./lib/mediaTypes";
import { connectMediaSocket } from "./lib/websocket";

function getDisplayId() {
    const params = new URLSearchParams(window.location.search);
    const rawValue = params.get("display") || params.get("dispaly") || "1";
    const display = Number(rawValue);

    return display === 2 ? 2 : 1;
}

function eventMatchesDisplay(event, displayId) {
    const mediaType = getMediaType(event);

    if (mediaType === MEDIA_TYPES.audio) {
        return displayId === 1;
    }

    return Number(event.display) === displayId;
}

function normalizeMediaEvent(event) {
    return {
        ...event,
        mediaType: getMediaType(event),
        filename: event.filename || event.path || event.src
    };
}

export default function App() {
    const displayId = useMemo(getDisplayId, []);
    const [visualMedia, setVisualMedia] = useState(null);
    const [audioMedia, setAudioMedia] = useState(null);

    useEffect(() => {
        return connectMediaSocket({
            onMessage: (event) => {
                if (event.type === "clear" && Number(event.display) === displayId) {
                    setVisualMedia(null);
                    return;
                }

                if (!isMediaEvent(event) || !eventMatchesDisplay(event, displayId)) {
                    return;
                }

                const media = normalizeMediaEvent(event);

                if (media.mediaType === MEDIA_TYPES.audio) {
                    setAudioMedia(media);
                    return;
                }

                setVisualMedia(media);
            }
        });
    }, [displayId]);

    return (
        <DisplayPane
            visualMedia={visualMedia}
            audioMedia={audioMedia}
            onVideoEnded={() => setVisualMedia(null)}
        />
    );
}
