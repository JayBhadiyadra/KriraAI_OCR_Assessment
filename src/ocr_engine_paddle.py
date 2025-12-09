# File already added earlier; ensuring import style is consistent
from __future__ import annotations

from typing import List

import numpy as np
from paddleocr import PaddleOCR

from src.utils import log


class PaddleOCREngine:
    def __init__(self, languages: list[str] | None = None, use_gpu: bool | None = None):
        langs = languages or ["en"]
        # Some PaddleOCR builds complain about unsupported params; keep it minimal.
        self.gpu = bool(use_gpu)
        log(f"initializing PaddleOCR (gpu={self.gpu}, langs={langs})")
        # try:
        #     # Most recent versions accept use_gpu, older ones ignore it; keep wrapped.
        #     self.reader = PaddleOCR(
        #         use_angle_cls=True,
        #         lang=langs[0],
        #         use_gpu=self.gpu,
        #     )
        # except TypeError:
        #     # Fallback for builds that don't support use_gpu kw.
        #     log("PaddleOCR init without use_gpu (fallback)")
        #     self.reader = PaddleOCR(
        #         use_angle_cls=True,
        #         lang=langs[0],
        #     )

        # Some builds of paddleocr reject use_gpu; to keep it stable, drop the arg.
        # If you want GPU, set it globally via paddle configs; here we stay portable.
        self.reader = PaddleOCR(
            use_angle_cls=True,
            lang=langs[0],
        )

    def run(self, image: np.ndarray, detail: bool = True):
        if image is None:
            raise ValueError("run() received None image")
        # Paddle expects RGB
        if image.ndim == 2:
            img = image
        else:
            # OpenCV is BGR; flip to RGB
            img = image[:, :, ::-1]
        result = self.reader.ocr(img, cls=True)
        # result is list per image; we process first entry
        if not result:
            return []
        lines = result[0]
        parsed: List[tuple] = []
        for line in lines:
            bbox, (text, conf) = line
            parsed.append((bbox, text, float(conf)))
        return parsed

