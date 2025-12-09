import io
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from process_dataset import run_with_backends
from src.ocr_engine import OCREngine
from src.ocr_engine_paddle import PaddleOCREngine
from src.ocr_engine_rapid import RapidOCREngine
from src.text_extraction import draw_highlight
from src.utils import detect_gpu, log


def pil_to_cv2(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def main():
    st.set_page_config(page_title="Waybill OCR", layout="wide")
    st.title("Waybill OCR (target line with `_1_`)")

    st.sidebar.header("Settings")
    gpu_available = detect_gpu()
    use_gpu = st.sidebar.checkbox("Use GPU (if available)", value=gpu_available)
    # backend = st.sidebar.radio("Backend", options=["rapid", "paddle", "easyocr"], index=2)
    backend = "easyocr"

    st.sidebar.write(f"GPU available: {gpu_available}")
    st.sidebar.caption("If things break, uncheck GPU to force CPU.")

    uploaded = st.file_uploader("Upload waybill image", type=["jpg", "png", "jpeg"])
    if uploaded is None:
        st.info("Drop a waybill image to get started.")
        return

    # log(f"received file: {uploaded.name}")
    file_bytes = uploaded.read()
    pil_img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    cv_img = pil_to_cv2(pil_img)

    # show a looping “in progress” indicator while OCR runs
    status = st.empty()
    dots = [" .", " ..", " ...", " ...."]
    result_holder = {}

    def worker():
        # Initialize engines once (reuse to avoid EP warnings)
        if backend == "paddle":
            primary_engine = PaddleOCREngine(use_gpu=use_gpu)
            fallback_engine = RapidOCREngine()
        elif backend == "easyocr":
            primary_engine = OCREngine(gpu=use_gpu)
            fallback_engine = RapidOCREngine()
        else:  # rapid
            primary_engine = RapidOCREngine()
            fallback_engine = OCREngine(gpu=use_gpu)
        
        best_local = run_with_backends(cv_img, primary_engine, fallback_engine)
        result_holder.update(best_local)

    t = threading.Thread(target=worker)
    t.start()
    i = 0
    while t.is_alive():
        status.info(f"OCR in progress{dots[i % len(dots)]}")
        time.sleep(0.25)
        i += 1
    t.join()
    status.empty()

    raw = result_holder.get("raw", [])
    extracted_text = result_holder.get("text")
    line = result_holder.get("line")
    overlay_img = result_holder.get("img", cv_img)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(pil_img, use_column_width=True)
    with col2:
        st.subheader("Highlighted result")
        overlay_rgb = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2RGB)
        overlay = draw_highlight(overlay_rgb, line) if line else overlay_rgb
        st.image(overlay, use_column_width=True)

    st.markdown("### Extracted text line")
    if extracted_text:
        st.success(extracted_text)
    else:
        st.warning("No line containing `_1_` found.")

    with st.expander("Raw OCR lines (debug)"):
        for bbox, text, conf in raw:
            st.write(f"{conf:.3f} | {text}")


if __name__ == "__main__":
    main()

