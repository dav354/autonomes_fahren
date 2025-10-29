from __future__ import annotations

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAME_RATE = 30
FLIP_METHOD = 0


def build_gstreamer_pipeline() -> str:
    """Erzeugt eine Pipeline, die das NV12-Signal in BGR konvertiert."""
    return (
        "nvarguscamerasrc ! "
        f"video/x-raw(memory:NVMM), width={FRAME_WIDTH}, height={FRAME_HEIGHT}, "
        f"format=NV12, framerate={FRAME_RATE}/1 ! "
        f"nvvidconv flip-method={FLIP_METHOD} ! "
        "video/x-raw, format=BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=BGR ! "
        "appsink drop=true sync=false"
    )


__all__ = [
    "FRAME_WIDTH",
    "FRAME_HEIGHT",
    "FRAME_RATE",
    "FLIP_METHOD",
    "build_gstreamer_pipeline",
]
