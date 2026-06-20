"""
Export best.pt to optimized inference formats for Intel CPU deployment.

Outputs:
  best.onnx              - ONNX FP32 (baseline)
  best_fp16.onnx         - ONNX FP16 (half precision)
  best_openvino_model/   - OpenVINO IR FP16 (fastest on Intel CPU)
"""

import os
import shutil
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "best.pt"


def get_size_mb(path: Path) -> float:
    if path.is_dir():
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1e6
    return path.stat().st_size / 1e6


def export_onnx_fp32() -> Path:
    print("\n[1/3] Exporting ONNX FP32...")
    model = YOLO(str(MODEL_PATH))
    model.export(format="onnx", half=False, dynamic=False, simplify=True)

    # ultralytics always writes to best.onnx — rename immediately so FP16 export won't overwrite it
    src = BASE_DIR / "best.onnx"
    dst = BASE_DIR / "best_fp32.onnx"
    if dst.exists():
        dst.unlink()
    shutil.move(str(src), str(dst))
    print(f"      Saved: {dst}  ({get_size_mb(dst):.1f} MB)")
    return dst


def export_onnx_fp16() -> Path:
    print("\n[2/3] Exporting ONNX FP16...")
    model = YOLO(str(MODEL_PATH))
    model.export(format="onnx", half=True, dynamic=False, simplify=True)

    # ultralytics writes to best.onnx — rename to best_fp16.onnx
    src = BASE_DIR / "best.onnx"
    dst = BASE_DIR / "best_fp16.onnx"
    if dst.exists():
        dst.unlink()
    shutil.move(str(src), str(dst))
    print(f"      Saved: {dst}  ({get_size_mb(dst):.1f} MB)")
    return dst


def export_openvino_fp16() -> Path:
    print("\n[3/3] Exporting OpenVINO FP16 (dynamic batch)...")
    model = YOLO(str(MODEL_PATH))
    # dynamic=True allows variable batch sizes at runtime (required for batch inference)
    model.export(format="openvino", half=True, dynamic=True)
    out = BASE_DIR / "best_openvino_model"
    print(f"      Saved: {out}/  ({get_size_mb(out):.1f} MB)")
    return out


def print_summary(fp32: Path, fp16: Path, ov: Path) -> None:
    print("\n" + "=" * 52)
    print(f"{'Format':<22} {'Size (MB)':>10} {'vs FP32':>10}")
    print("-" * 52)

    fp32_mb = get_size_mb(fp32)
    fp16_mb = get_size_mb(fp16)
    ov_mb   = get_size_mb(ov)

    print(f"{'ONNX FP32 (best_fp32)':<22} {fp32_mb:>10.1f} {'(baseline)':>10}")
    print(f"{'ONNX FP16 (best_fp16)':<22} {fp16_mb:>10.1f} {f'-{(1 - fp16_mb/fp32_mb)*100:.0f}%':>10}")
    print(f"{'OpenVINO FP16':<22} {ov_mb:>10.1f} {f'-{(1 - ov_mb/fp32_mb)*100:.0f}%':>10}")
    print("=" * 52)
    print("\nEngine priority at runtime:  OpenVINO FP16 > ONNX FP16 > ONNX FP32")


if __name__ == "__main__":
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    print(f"Source model : {MODEL_PATH}  ({get_size_mb(MODEL_PATH):.1f} MB)")

    fp32_path = export_onnx_fp32()
    fp16_path = export_onnx_fp16()
    ov_path   = export_openvino_fp16()

    print_summary(fp32_path, fp16_path, ov_path)
