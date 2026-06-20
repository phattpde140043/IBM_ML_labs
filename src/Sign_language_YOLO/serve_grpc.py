import cv2
import numpy as np
import torch
import grpc
from concurrent import futures
import yolo_pb2
import yolo_pb2_grpc
from ultralytics import YOLO
import sys

class YoloServicer(yolo_pb2_grpc.YoloServiceServicer):
    def __init__(self, model_path="best.pt"):
        # Cấu hình tối ưu GPU theo yêu cầu đề bài
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
            
        print(f"[AI Server] Khởi tạo Model trên thiết bị: {self.device.upper()}")
        
        try:
            self.model = YOLO(model_path)
            self.model.to(self.device)
        except Exception as e:
            print(f"[AI Server] Lỗi khởi tạo model: {e}")
            sys.exit(1)

    def StreamPredict(self, request_iterator, context):
        print("[AI Server] Có Client Ingestion kết nối tới!")
        # Luồng Bi-directional: Nhận ảnh liên tục và trả kết quả liên tục
        for request in request_iterator:
            # 1. Giải nén ảnh JPEG thành mảng OpenCV
            np_arr = np.frombuffer(request.image_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                continue

            # 2. Xử lý suy luận trên GPU (Bật verbose=True để hiển thị log phân tích)
            # Giảm conf xuống 0.25 để AI dễ dàng bắt được nhiều vật thể mờ/nhỏ hơn trong cùng khung hình
            results = self.model(frame, conf=0.25, verbose=False)
            
            # 3. Đóng gói kết quả Bounding Box vào gRPC Message
            result_msg = yolo_pb2.InferenceResult()
            result_msg.timestamp = request.timestamp
            
            if results and results[0].boxes:
                for box in results[0].boxes:
                    b = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    
                    bbox_msg = result_msg.boxes.add()
                    bbox_msg.x1 = b[0]
                    bbox_msg.y1 = b[1]
                    bbox_msg.x2 = b[2]
                    bbox_msg.y2 = b[3]
                    bbox_msg.confidence = conf
                    bbox_msg.label = f"{self.model.names[cls]}"
            
            # Trả kết quả về cho Client ngay lập tức
            yield result_msg
            
        print("[AI Server] Client đã ngắt kết nối.")

def serve():
    # Giới hạn 10 luồng xử lý đồng thời
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    yolo_pb2_grpc.add_YoloServiceServicer_to_server(YoloServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("[AI Server] AI Model Serving đang chạy (Tối ưu GPU) trên cổng 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
