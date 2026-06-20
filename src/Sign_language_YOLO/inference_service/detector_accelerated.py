"""
Accelerated inference core for Sign Language YOLO.

Auto-detects and loads the best available engine in priority order:
  1. OpenVINO FP16  (fastest on Intel CPU)
  2. ONNX FP16      (half-precision, cross-platform)
  3. ONNX FP32      (full-precision fallback)
  4. PyTorch .pt    (last resort — no compilation benefit)

Run export_accelerated.py first to generate compiled engines.
"""

from pathlib import Path
from typing import TypedDict

import numpy as np
from ultralytics import YOLO

BASE_DIR = Path(__file__).parent.parent  # Sign_language_YOLO/

ENGINE_PRIORITY = [
    ("OpenVINO FP16", BASE_DIR / "best_openvino_model"),
    ("ONNX FP16",     BASE_DIR / "best_fp16.onnx"),
    ("ONNX FP32",     BASE_DIR / "best_fp32.onnx"),
    ("PyTorch",       BASE_DIR / "best.pt"),
]


class Detection(TypedDict):
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    label: str


class AcceleratedDetector:
    def __init__(self) -> None:
        self.model, self.engine_name = self._load_best_engine()

    def _load_best_engine(self) -> tuple:
        for name, path in ENGINE_PRIORITY:
            if path.exists():
                print(f"[Detector] Loading engine  : {name}")
                print(f"[Detector] Path            : {path}")
                model = YOLO(str(path), task="detect")
                print(f"[Detector] Engine ready    : {name}")
                return model, name
        raise RuntimeError(
            "No compiled engine found. Run export_accelerated.py first."
        )

    def predict_batch(self, frames: list[np.ndarray]) -> list[list[Detection]]:
        """Run inference on a batch of BGR frames.

        Args:
            frames: List of numpy arrays in BGR format (from cv2).

        Returns:
            List of detection lists — one per input frame.
        """
        if not frames:
            return []

        results = self.model(frames, conf=0.25, verbose=False)
        return [self._parse_result(r) for r in results]

    def _parse_result(self, result) -> list[Detection]:
        detections: list[Detection] = []
        if result.boxes is None:
            return detections
        for box in result.boxes:
            b = box.xyxy[0].cpu().numpy().astype(int)
            detections.append(
                Detection(
                    x1=int(b[0]),
                    y1=int(b[1]),
                    x2=int(b[2]),
                    y2=int(b[3]),
                    confidence=float(box.conf[0]),
                    label=result.names[int(box.cls[0])],
                )
            )
        return detections
