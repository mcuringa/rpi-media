export const MEDIA_TYPES = {
    image: "image",
    video: "video",
    audio: "audio"
};

export function getMediaType(event) {
    return event?.mediaType || (event?.kind === "img" ? MEDIA_TYPES.image : event?.kind);
}

export function isMediaEvent(event) {
    return event?.type === "media" && Boolean(getMediaType(event)) && Boolean(event.filename || event.path || event.src);
}
