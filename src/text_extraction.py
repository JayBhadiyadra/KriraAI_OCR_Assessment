from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np

# pattern we care about: a line containing "_1_"
TARGET_REGEX = re.compile(r"_1_", flags=re.IGNORECASE)


@dataclass
class OCRLine:
    bbox: Sequence[Sequence[float]]
    text: str
    confidence: float


def clean_text(text: str) -> str:
    return text.replace("\n", " ").strip()


def parse_results(raw_results) -> List[OCRLine]:
    parsed: List[OCRLine] = []
    for item in raw_results:
        if len(item) != 3:
            continue
        bbox, txt, conf = item
        parsed.append(OCRLine(bbox=bbox, text=clean_text(txt), confidence=float(conf)))
    return parsed


def pick_target_line(lines: List[OCRLine]) -> Optional[OCRLine]:
    """
    Find the line that contains our _1_ marker.
    Strategy: pick the highest-confidence line that matches the regex.
    """
    candidates = [ln for ln in lines if TARGET_REGEX.search(ln.text)]
    if candidates:
        return max(candidates, key=lambda ln: ln.confidence)

    # fallback: sometimes the OCR splits underscores; try a softer check
    # loose_candidates = [ln for ln in lines if "1" in ln.text and "_" in ln.text]
    loose_candidates = [ln for ln in lines if "_1" in ln.text]
    if loose_candidates:
        return max(loose_candidates, key=lambda ln: ln.confidence)
    return None


def draw_highlight(image: np.ndarray, line: OCRLine) -> np.ndarray:
    """
    Draw a visible rectangle around the chosen line for the Streamlit preview.
    """
    if line is None:
        return image
    overlay = image.copy()
    # bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    pts = np.array(line.bbox, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(overlay, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    cv2.putText(
        overlay,
        line.text[:40],
        (pts[0][0][0], max(0, pts[0][0][1] - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    return overlay


def extract_target_text(raw_results) -> Tuple[Optional[str], Optional[OCRLine]]:
    lines = parse_results(raw_results)
    target = pick_target_line(lines)
    if target:
        return target.text, target
    return None, None


