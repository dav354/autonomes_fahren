import time
from datetime import datetime
from pathlib import Path

import cv2 as cv

COUNT = 20  # Anzahl der Bilder
DELAY = 3.0  # Pause zwischen den Aufnahmen in Sekunden
OUTPUT_DIR = Path("assets/calibration")  # Basisverzeichnis
CAMERA_INDEX = 0  # Kameraindex für cv.VideoCapture


def main() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = OUTPUT_DIR / timestamp
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Speichere Bilder unter: {target_dir}")
    print(f"[INFO] Öffne Kamera mit Index {CAMERA_INDEX} ...")

    capture = cv.VideoCapture(CAMERA_INDEX)
    if not capture.isOpened():
        raise SystemExit(f"[FEHLER] Kamera {CAMERA_INDEX} konnte nicht geöffnet werden.")

    try:
        time.sleep(1.0) 

        for idx in range(1, COUNT + 1):
            ret, frame = capture.read()
            if not ret or frame is None:
                print(f"[WARNUNG] Kein Bild bei Aufnahme {idx}, überspringe.")
                time.sleep(DELAY)
                continue

            filename = target_dir / f"image_{idx:03d}.jpg"
            cv.imwrite(str(filename), frame)
            print(f"[OK] Gespeichert: {filename}")

            if idx < COUNT:
                print(f"[INFO] Warte {DELAY:.1f} Sekunden bis zur nächsten Aufnahme ...")
                time.sleep(DELAY)

        print("[INFO] Aufnahme abgeschlossen.")
    finally:
        capture.release()


if __name__ == "__main__":
    main()
