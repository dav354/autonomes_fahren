from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import cv2 as cv

from autonomes_fahren.camera import build_gstreamer_pipeline
from autonomes_fahren.stream import start_stream, stop_stream

COUNT = 20  # Anzahl der Bilder
DELAY = 3.0  # Pause zwischen den Aufnahmen in Sekunden
OUTPUT_DIR = Path("assets/calibration")  # Basisverzeichnis für Fotos
START_STREAM = True  # MJPEG-Stream parallel starten?
STREAM_START_DELAY = 10.0  # Warten nach Stream-Start (Sekunden)
PIPELINE = build_gstreamer_pipeline()


def main() -> None:
    stream_proc = start_stream() if START_STREAM else None
    if stream_proc:
        print(f"[INFO] Warte {STREAM_START_DELAY:.1f}s bis zur ersten Aufnahme ...")
        time.sleep(STREAM_START_DELAY)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = OUTPUT_DIR / timestamp
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Speichere Bilder unter: {target_dir}")

    capture = cv.VideoCapture(PIPELINE, cv.CAP_GSTREAMER)
    if not capture.isOpened():
        stop_stream(stream_proc)
        raise SystemExit("[FEHLER] Kamera-Pipeline konnte nicht geöffnet werden.")

    try:
        for idx in range(1, COUNT + 1):
            ret, frame = capture.read()
            if not ret or frame is None:
                print(f"[WARNUNG] Kein Bild bei Aufnahme {idx}, überspringe.")
                time.sleep(DELAY)
                continue

            filename = target_dir / f"image_{idx:03d}.jpg"
            if cv.imwrite(str(filename), frame):
                print(f"[OK] Gespeichert: {filename}")
            else:
                print(f"[FEHLER] Schreiben von {filename} fehlgeschlagen.")

            if idx < COUNT:
                print(
                    f"[INFO] Warte {DELAY:.1f} Sekunden bis zur nächsten Aufnahme ..."
                )
                time.sleep(DELAY)

        print("[INFO] Aufnahme abgeschlossen.")
    finally:
        capture.release()
        stop_stream(stream_proc)


if __name__ == "__main__":
    main()
