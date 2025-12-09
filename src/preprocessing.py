from __future__ import annotations

import cv2
import numpy as np

from src.utils import log


def estimate_skew_angle(gray: np.ndarray) -> float:
    """
    Estimate document skew using Hough lines. We keep it conservative:
    only return small angles so we don't over-rotate good images.
    """
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=120)
    if lines is None:
        return 0.0

    angles = []
    for line in lines[:30]:  # use a handful to stay fast
        rho, theta = line[0]
        angle = (theta * 180 / np.pi) - 90
        # ignore near-vertical lines; we only care about horizontal drift
        if -20 < angle < 20:
            angles.append(angle)
    if not angles:
        return 0.0
    median_angle = float(np.median(angles))
    return median_angle


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image,
        mat,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated


def preprocess_image(
    image: np.ndarray,
    do_clahe: bool = True,
    do_denoise: bool = True,
    do_deskew: bool = True,
    return_gray: bool = False,
) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
    """
    Light-touch preprocessing tuned for shipping labels:
    - convert to gray
    - optional CLAHE for contrast
    - gentle denoise
    - optional deskew for mild rotations
    """
    if image is None:
        raise ValueError("preprocess_image received None image")

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    if do_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

    if do_denoise:
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

    if do_deskew:
        angle = estimate_skew_angle(gray)
        if abs(angle) > 0.8:  # tiny angles are usually noise
            log(f"deskewing by {angle:.2f} degrees")
            gray = rotate_image(gray, angle)

    # final gentle threshold to sharpen text
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    if return_gray:
        return gray, binary
    return binary


