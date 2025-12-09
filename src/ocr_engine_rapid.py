from __future__ import annotations

import numpy as np
from rapidocr_onnxruntime import RapidOCR

from src.utils import log


class RapidOCREngine:
    def __init__(self):
        log("initializing RapidOCR (onnxruntime)")
        self.reader = RapidOCR(
            det_use_cuda=False,
            rec_use_cuda=False,
            providers=["CPUExecutionProvider"],
        )

    def run(self, image: np.ndarray, detail: bool = True):
        if image is None:
            raise ValueError("run() received None image")
        res, _ = self.reader(image)
        if res is None:
            return []
        parsed = []
        for box, text, conf in res:
            parsed.append((box, text, float(conf)))
        return parsed

