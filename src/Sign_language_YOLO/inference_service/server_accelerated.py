"""
Batched gRPC server for Sign Language YOLO (Lab 2).

Implements BatchPredict RPC: receives a BatchVideoFrame containing multiple
JPEG-encoded frames, runs them through AcceleratedDetector in a single forward
pass, and returns a BatchInferenceResult.

StreamPredict from Lab 1 is preserved via delegation to the original servicer.
"""

import sys
from pathlib import Path
from concurrent import futures

import cv2
import grpc
import numpy as np

# Allow imports of proto files located in the project root
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import yolo_pb2
import yolo_pb2_grpc
from inference_service.detector_accelerated import AcceleratedDetector


def _decode_jpeg(image_data: bytes) -> np.ndarray | None:
    np_arr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame  # None if decoding failed


class AcceleratedYoloServicer(yolo_pb2_grpc.YoloServiceServicer):
    def __init__(self) -> None:
        self.detector = AcceleratedDetector()
        print(f"[Server] Engine: {self.detector.engine_name}")

    # ------------------------------------------------------------------
    # Lab 1 — preserved, unchanged
    # ------------------------------------------------------------------
    def StreamPredict(self, request_iterator, context):
        print("[Server] StreamPredict client connected")
        for request in request_iterator:
            frame = _decode_jpeg(request.image_data)
            if frame is None:
                continue
            batch_results = self.detector.predict_batch([frame])
            detections = batch_results[0] if batch_results else []

            result_msg = yolo_pb2.InferenceResult(
                timestamp=request.timestamp,
                camera_id=request.camera_id,
            )
            for d in detections:
                bbox = result_msg.boxes.add()
                bbox.x1, bbox.y1 = d["x1"], d["y1"]
                bbox.x2, bbox.y2 = d["x2"], d["y2"]
                bbox.confidence = d["confidence"]
                bbox.label = d["label"]
            yield result_msg
        print("[Server] StreamPredict client disconnected")

    # ------------------------------------------------------------------
    # Lab 2 — batch unary RPC
    # ------------------------------------------------------------------
    def BatchPredict(self, request, context):
        if not request.frames:
            return yolo_pb2.BatchInferenceResult()

        # Decode all frames; track which indices are valid
        frames, index_map = [], []
        for i, vf in enumerate(request.frames):
            frame = _decode_jpeg(vf.image_data)
            if frame is not None:
                frames.append(frame)
                index_map.append(i)

        if not frames:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("All frames in batch failed to decode.")
            return yolo_pb2.BatchInferenceResult()

        batch_detections = self.detector.predict_batch(frames)

        # Build response — one InferenceResult per original frame
        response = yolo_pb2.BatchInferenceResult()
        for detections, orig_idx in zip(batch_detections, index_map):
            vf = request.frames[orig_idx]
            result_msg = yolo_pb2.InferenceResult(
                timestamp=vf.timestamp,
                camera_id=vf.camera_id,
            )
            for d in detections:
                bbox = result_msg.boxes.add()
                bbox.x1, bbox.y1 = d["x1"], d["y1"]
                bbox.x2, bbox.y2 = d["x2"], d["y2"]
                bbox.confidence = d["confidence"]
                bbox.label = d["label"]
            response.results.append(result_msg)

        return response


def serve(port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    yolo_pb2_grpc.add_YoloServiceServicer_to_server(
        AcceleratedYoloServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    print(f"[Server] Accelerated batch server listening on port {port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
