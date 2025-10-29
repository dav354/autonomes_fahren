"""Kalibrierung der Kamera mit Schachbrettaufnahmen und Entzerrung eines Beispiels.

Ablauf:
1. Kalibrierbilder aufnehmen (auf JetBot oder Laptop).
2. Ecken erkennen und zur Kontrolle einblenden.
3. Kameramatrix sowie Verzerrungskoeffizienten bestimmen.
4. Ein Beispielbild entzerren und optional abspeichern.
"""

from __future__ import annotations

import argparse
import glob
from pathlib import Path
from typing import Sequence

import cv2 as cv
import numpy as np


def collect_chessboard_points(
    image_paths: Sequence[str], pattern_size: tuple[int, int], show: bool
) -> tuple[list[np.ndarray], list[np.ndarray], tuple[int, int], np.ndarray]:
    """Erkenne Schachbrettecken in allen Bildern und sammle Objekt- und Bildpunkte."""
    # 3D-Koordinaten des Schachbretts (Quadratgröße = 1 Einheit -> später skalierbar).
    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : pattern_size[0], 0 : pattern_size[1]].T.reshape(-1, 2)

    objpoints: list[np.ndarray] = []  # 3D-Punkte im Weltkoordinatensystem
    imgpoints: list[np.ndarray] = []  # 2D-Projektionspunkte im Bild
    last_gray_shape: tuple[int, int] | None = None
    last_image: np.ndarray | None = None

    # Abbruchkriterium für cornerSubPix (Verfeinerung der Eckpunkte).
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for path in image_paths:
        image = cv.imread(path)
        if image is None:
            print(f"Warnung: Bild {path} konnte nicht geladen werden.")
            continue

        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        found, corners = cv.findChessboardCorners(gray, pattern_size, None)

        if not found:
            print(f"Keine Schachbrettecken in {path} gefunden.")
            continue

        refined_corners = cv.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria
        )

        objpoints.append(objp.copy())
        imgpoints.append(refined_corners)
        last_gray_shape = gray.shape[::-1]
        last_image = image

        if show:
            preview = image.copy()
            cv.drawChessboardCorners(preview, pattern_size, refined_corners, found)
            cv.imshow("Schachbrett-Erkennung", preview)
            cv.waitKey(300)

    if show:
        cv.destroyAllWindows()

    if not objpoints or not imgpoints or last_gray_shape is None or last_image is None:
        raise RuntimeError(
            "Es konnten keine gültigen Kalibrierbilder verarbeitet werden."
        )

    return objpoints, imgpoints, last_gray_shape, last_image


def calibrate_camera(
    objpoints: list[np.ndarray], imgpoints: list[np.ndarray], image_size: tuple[int, int]
) -> tuple[float, np.ndarray, np.ndarray, list[np.ndarray], list[np.ndarray]]:
    """Berechne Kameramatrix und Verzerrungskoeffizienten."""
    rms, camera_matrix, dist_coeffs, rvecs, tvecs = cv.calibrateCamera(
        objpoints, imgpoints, image_size, None, None
    )
    return rms, camera_matrix, dist_coeffs, rvecs, tvecs


def undistort_sample(
    image: np.ndarray, camera_matrix: np.ndarray, dist_coeffs: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Entzerre ein Beispielbild und gib das neue Kameramatrix-FOV zurück."""
    height, width = image.shape[:2]
    new_camera_matrix, _roi = cv.getOptimalNewCameraMatrix(
        camera_matrix, dist_coeffs, (width, height), 1, (width, height)
    )
    undistorted = cv.undistort(image, camera_matrix, dist_coeffs, None, new_camera_matrix)
    return undistorted, new_camera_matrix


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kalibrierung einer Kamera mit Schachbrettaufnahmen."
    )
    parser.add_argument(
        "--pattern-columns",
        type=int,
        default=7,
        help="Anzahl innerer Ecken pro Reihe (Standard: 7).",
    )
    parser.add_argument(
        "--pattern-rows",
        type=int,
        default=6,
        help="Anzahl innerer Ecken pro Spalte (Standard: 6).",
    )
    parser.add_argument(
        "--images",
        default="*.jpg",
        help="Glob-Muster für Kalibrierbilder (z. B. 'data/calib/*.jpg').",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Keine Fenster zur visuellen Kontrolle anzeigen.",
    )
    parser.add_argument(
        "--save-undistorted",
        type=Path,
        default=None,
        help="Entzerrtes Beispielbild speichern (Pfad angeben).",
    )
    args = parser.parse_args()

    image_paths = sorted(glob.glob(args.images))
    if not image_paths:
        raise SystemExit(f"Keine Bilder gefunden für Muster: {args.images}")

    pattern_size = (args.pattern_columns, args.pattern_rows)
    objpoints, imgpoints, image_size, sample_image = collect_chessboard_points(
        image_paths,
        pattern_size,
        show=not args.no_display,
    )

    rms, camera_matrix, dist_coeffs, _rvecs, _tvecs = calibrate_camera(
        objpoints, imgpoints, image_size
    )

    print("Kalibrierung abgeschlossen:")
    print(f"  RMS-Reprojektionsfehler: {rms:.4f}")
    print("  Kameramatrix:")
    print(camera_matrix)
    print("  Verzerrungskoeffizienten (k1, k2, p1, p2, k3):")
    print(dist_coeffs.ravel())

    undistorted, new_camera_matrix = undistort_sample(
        sample_image, camera_matrix, dist_coeffs
    )
    print("Optimierte Kameramatrix für Entzerrung:")
    print(new_camera_matrix)

    if not args.no_display:
        cv.imshow("Entzerrtes Beispiel", undistorted)
        print("Fenster schließen mit beliebiger Taste...")
        cv.waitKey(0)
        cv.destroyAllWindows()

    if args.save_undistorted is not None:
        args.save_undistorted.parent.mkdir(parents=True, exist_ok=True)
        cv.imwrite(str(args.save_undistorted), undistorted)
        print(f"Entzerrtes Bild gespeichert unter: {args.save_undistorted}")

    # Kalibrierung auf Wunsch dauerhaft sichern.
    np.savez(
        "camera_calibration.npz",
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        new_camera_matrix=new_camera_matrix,
        rms=rms,
    )
    print("Kalibrierdaten gespeichert in camera_calibration.npz.")


if __name__ == "__main__":
    main()
