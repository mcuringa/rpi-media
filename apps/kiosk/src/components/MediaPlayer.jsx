import React, { useEffect, useRef } from "react";

import { MEDIA_TYPES } from "../lib/mediaTypes";
import { resolveMediaSrc } from "../lib/websocket";

function playMediaElement(element, label) {
    const playPromise = element.play();

    if (playPromise) {
        playPromise.catch((error) => {
            console.warn(`${label} playback did not start`, error);
        });
    }
}

export default function MediaPlayer({ media, onVideoEnded }) {
    const videoRef = useRef(null);
    const audioRef = useRef(null);
    const mediaSrc = media ? resolveMediaSrc(media.mediaType, media.filename) : "";

    useEffect(() => {
        if (media?.mediaType !== MEDIA_TYPES.video || !videoRef.current) {
            return;
        }

        const video = videoRef.current;
        video.load();
        playMediaElement(video, "Video");
    }, [media, mediaSrc]);

    useEffect(() => {
        if (media?.mediaType !== MEDIA_TYPES.audio || !audioRef.current) {
            return;
        }

        const audio = audioRef.current;
        audio.load();
        playMediaElement(audio, "Audio");
    }, [media, mediaSrc]);

    if (!media) {
        return null;
    }

    if (media.mediaType === MEDIA_TYPES.image) {
        return <img className="media media-image" src={mediaSrc} alt="" />;
    }

    if (media.mediaType === MEDIA_TYPES.video) {
        return (
            <video
                key={mediaSrc}
                ref={videoRef}
                className="media media-video"
                src={mediaSrc}
                playsInline
                autoPlay
                preload="auto"
                onCanPlay={() => {
                    if (videoRef.current?.paused) {
                        playMediaElement(videoRef.current, "Video");
                    }
                }}
                onEnded={onVideoEnded}
            />
        );
    }

    if (media.mediaType === MEDIA_TYPES.audio) {
        return <audio ref={audioRef} src={mediaSrc} autoPlay />;
    }

    return null;
}
