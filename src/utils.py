from pathlib import Path
import torch


def detect_gpu() -> bool:
    """
    Decide if GPU is available for OCR. EasyOCR benefits from CUDA but we
    keep a safe CPU fallback so the script still runs on any machine.
    """
    try:
        gpu_ok = torch.cuda.is_available()
        # quick sanity check because sometimes drivers are flaky
        if gpu_ok and torch.cuda.device_count() > 0:
            return True
    except Exception:
        # keep it simple: if anything feels off, stay on CPU to avoid crashes
        return False
    return False


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_image_path(path: str | Path) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    return p.resolve()


# little helper for logging
def log(msg: str) -> None:
    print(f"[debug] {msg}")


