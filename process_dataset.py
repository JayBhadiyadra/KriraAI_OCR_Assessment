import argparse
import cv2
import json
from pathlib import Path

from src.ocr_engine import OCREngine
from src.ocr_engine_paddle import PaddleOCREngine
from src.ocr_engine_rapid import RapidOCREngine
from src.preprocessing import preprocess_image
from src.text_extraction import draw_highlight, extract_target_text
from src.utils import ensure_dir, load_image_path, log


def rotate_variants(image):
    """
    Optimized rotations: orig + rot90 covers most cases, faster than 4 rotations.
    For edge cases, added more rotations like rot270 and rot180.
    """
    return [
        ("orig", image),
        ("rot90", cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)),
        ("rot270", cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)),
        ("rot180", cv2.rotate(image, cv2.ROTATE_180)),
    ]


def preprocess_variants(img: cv2.UMat) -> list[tuple[str, cv2.UMat]]:
    """
    Optimized preprocessing: keep only essential variants for speed.
    """
    variants = []
    gray, binary = preprocess_image(img, return_gray=True)

    # base binary (most common case)
    variants.append(("bin", binary))

    # light dilation for broken underscores
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilated = cv2.dilate(binary, kernel, iterations=1)
    variants.append(("dilate", dilated))

    # keep gray as fallback
    variants.append(("gray", gray))

    return variants


def run_with_backends(image, primary_engine, fallback_engine=None):
    """
    Shared OCR routine: try primary backend, then fallback, across
    rotations and preprocess variants. Returns best text/line/variant/raw.
    Optimized for speed: 2 rotations × 3 preprocess variants = 6 attempts max.
    Engines are passed in to avoid re-initialization (fixes RapidOCR EP warnings).
    """
    best = {"text": None, "line": None, "conf": -1.0, "variant": "orig", "raw": None, "img": image}

    def try_engine(engine, tag):
        nonlocal best
        for variant_name, variant_img in rotate_variants(image):
            for prep_name, prep in preprocess_variants(variant_img):
                raw = engine.run(prep)
                extracted_text, line = extract_target_text(raw)
                if line and line.confidence > best["conf"]:
                    best.update(
                        {
                            "text": extracted_text,
                            "line": line,
                            "conf": line.confidence,
                            "variant": f"{tag}-{variant_name}-{prep_name}",
                            "raw": raw,
                            "img": variant_img,
                        }
                    )

    try_engine(primary_engine, "primary")
    if best["text"] is None and fallback_engine:
        try_engine(fallback_engine, "fallback")

    return best


def process_folder(
    input_dir: Path,
    output_dir: Path,
    use_gpu: bool | None = None,
    backend: str = "rapid",
):
    ensure_dir(output_dir)
    overlay_dir = ensure_dir(output_dir / "overlays")

    # Initialize engines once (reuse across all images to avoid EP warnings)
    log(f"initializing engines for backend: {backend}")
    if backend == "paddle":
        primary_engine = PaddleOCREngine(use_gpu=use_gpu)
        fallback_engine = RapidOCREngine()
    elif backend == "easyocr":
        primary_engine = OCREngine(gpu=use_gpu)
        fallback_engine = RapidOCREngine()
    else:  # rapid default
        primary_engine = RapidOCREngine()
        fallback_engine = OCREngine(gpu=use_gpu)

    results = {}
    for img_path in sorted(input_dir.glob("*.jpg")):
        try:
            log(f"processing {img_path.name}")
            image_path = load_image_path(img_path)
            image = cv2.imread(str(image_path))
            if image is None:
                log(f"could not read {img_path}, skipping")
                continue

            best = run_with_backends(image, primary_engine, fallback_engine)

            # fallback: keep something even if no target found
            final_text = best["text"]
            # # enforce marker presence; otherwise treat as miss
            # if final_text is None or "_1_" not in final_text:
            #     final_text = None
            found = final_text is not None
            results[img_path.name] = {
                "extracted_text": final_text,
                "found": found,
                "variant": best["variant"],
                "confidence": best["conf"],
                # "bbox": best["line"].bbox if best["line"] else None,
                # "raw_lines": best["raw"],
            }
            # total += 1
            # hits += 1 if found else 0

            # store overlay with highlight (use best variant image if available)
            overlay_source = best.get("img", image)
            overlay_img = draw_highlight(overlay_source, best["line"]) if best["line"] else overlay_source
            out_path = overlay_dir / f"{img_path.stem}_overlay.jpg"
            cv2.imwrite(str(out_path), overlay_img)
        except Exception as exc:
            log(f"error on {img_path.name}: {exc}")
            results[img_path.name] = {"extracted_text": None, "found": False, "error": str(exc)}

    # accuracy = hits / total if total else 0.0
    # results["__metrics__"] = {
    #     "total_images": total,
    #     "hits_with__1__": hits,
    #     "accuracy": round(accuracy, 4),
    # }

    out_json = output_dir / "predictions.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    # log(f"saved predictions to {out_json} (acc={accuracy:.3f})")


def main():
    parser = argparse.ArgumentParser(description="Batch OCR for ReverseWay Bill dataset.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("ReverseWay_Bill"),
        help="Folder containing waybill images",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Folder to dump predictions/overlays",
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Force GPU mode (will fallback to CPU if CUDA missing)",
    )
    parser.add_argument(
        "--backend",
        choices=["rapid", "paddle", "easyocr"],
        default="rapid",
        help="OCR backend to use",
    )
    args = parser.parse_args()

    process_folder(args.data_dir, args.output_dir, use_gpu=args.gpu, backend=args.backend)


if __name__ == "__main__":
    main()

