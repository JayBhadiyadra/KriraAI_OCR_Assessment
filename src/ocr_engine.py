from __future__ import annotations

import easyocr
import numpy as np

from src.utils import detect_gpu, log


class OCREngine:
    def __init__(self, languages: list[str] | None = None, gpu: bool | None = None):
        langs = languages or ["en"]
        if gpu is None:
            gpu = detect_gpu()
        self.gpu = gpu
        log(f"initializing EasyOCR (gpu={self.gpu}, langs={langs})")
        self.reader = easyocr.Reader(langs, gpu=self.gpu, verbose=False)

    def run(self, image: np.ndarray, detail: bool = True):
        if image is None:
            raise ValueError("run() received None image")
        # leaving contrast_ths default; tuning can be done later
        return self.reader.readtext(
            image,
            detail=detail,
            paragraph=False,
            decoder="beamsearch",  # slightly better accuracy, slower is fine here
        )

    def run_multi(self, images: list[np.ndarray]) -> list:
        """
        Convenience: run OCR on multiple processed variants and aggregate.
        """
        all_results = []
        for idx, img in enumerate(images):
            log(f"ocr pass {idx+1}/{len(images)}")
            all_results.append(self.run(img))
        return all_results


