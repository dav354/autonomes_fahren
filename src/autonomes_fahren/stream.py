from __future__ import annotations

import subprocess
import sys
import time
from typing import Optional

from autonomes_fahren.camera import build_gstreamer_pipeline

PORT = 8080
STARTUP_WAIT = 1.0  # Sekunden warten, bis mjpegserver bereit ist
PIPELINE = build_gstreamer_pipeline()


def build_command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "mjpegserver",
        "--port",
        str(PORT),
        "--pipeline",
        PIPELINE,
    ]


def start_stream() -> subprocess.Popen:
    cmd = build_command()
    print(f"[INFO] Starte mjpegserver: {' '.join(cmd[1:])}")
    print(f"[INFO] Stream erreichbar unter -> http://<IP>:{PORT}")
    proc = subprocess.Popen(cmd)
    time.sleep(STARTUP_WAIT)
    if proc.poll() is not None:
        raise RuntimeError("mjpegserver konnte nicht gestartet werden. Logs prüfen.")
    return proc


def stop_stream(proc: Optional[subprocess.Popen]) -> None:
    if proc is None:
        return
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> None:
    try:
        proc = start_stream()
        proc.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Stream durch Benutzer beendet.")
        stop_stream(proc if "proc" in locals() else None)


if __name__ == "__main__":
    main()
