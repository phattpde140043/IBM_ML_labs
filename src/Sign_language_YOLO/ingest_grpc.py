import cv2
import grpc
import threading
import sys
import yolo_pb2
import yolo_pb2_grpc

class WebcamStream:
    """Thread 1: Đọc ảnh liên tục từ Webcam (Producer)"""
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            sys.exit(1)
        self.ret, self.frame = self.cap.read()
        if self.ret:
            self.frame = cv2.flip(self.frame, 1)
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                break
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                with self.lock:
                    self.ret = ret
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy()

    def stop(self):
        self.stopped = True
        self.cap.release()

class GrpcWorker:
    """Thread 2: Đẩy ảnh qua gRPC và nhận kết quả (Network Worker)"""
    def __init__(self, target='localhost:50051'):
        self.channel = grpc.insecure_channel(target)
        self.stub = yolo_pb2_grpc.YoloServiceStub(self.channel)

        self.frame_to_process = None
        self.latest_boxes = None
        self.stopped = False
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        # Backpressure control: chỉ gửi frame mới sau khi nhận kết quả frame trước
        self.ready = threading.Event()
        self.ready.set()

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()
        return self

    def set_frame(self, frame):
        """Đẩy frame vào hàng chờ truyền mạng"""
        with self.cond:
            self.frame_to_process = frame
            self.cond.notify()

    def get_results(self):
        """Lấy kết quả mạng mới nhất"""
        with self.lock:
            return self.latest_boxes

    def _request_generator(self):
        """Generator đẩy dữ liệu qua luồng Bi-directional gRPC"""
        while not self.stopped:
            # Chờ server trả kết quả frame trước — tránh tích lũy backlog
            self.ready.wait()
            if self.stopped:
                break

            with self.cond:
                self.cond.wait_for(lambda: self.frame_to_process is not None or self.stopped)
                if self.stopped:
                    break
                frame = self.frame_to_process
                self.frame_to_process = None

            if frame is not None:
                self.ready.clear()  # Khoá lại cho đến khi nhận được response
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                yield yolo_pb2.VideoFrame(image_data=buffer.tobytes(), timestamp=0)

    def run(self):
        """Vòng lặp ngầm quản lý kết nối mạng"""
        while not self.stopped:
            try:
                self.ready.set()  # Reset khi reconnect để tránh deadlock
                responses = self.stub.StreamPredict(self._request_generator(), wait_for_ready=True)
                for response in responses:
                    if self.stopped:
                        break
                    with self.lock:
                        self.latest_boxes = response.boxes
                    self.ready.set()  # Mở khoá — sẵn sàng gửi frame tiếp theo
            except grpc.RpcError as e:
                if self.stopped:
                    break
                self.ready.set()  # Mở khoá khi lỗi để tránh deadlock
                print(f"[Client] Lỗi kết nối gRPC, đang thử lại sau 2 giây... (Chi tiết: {e.details()})")
                import time
                time.sleep(2)

    def stop(self):
        with self.cond:
            self.stopped = True
            self.cond.notify()
        self.ready.set()  # Mở khoá generator nếu đang chờ
        self.channel.close()

def main():
    print("Starting Stream Ingestion via gRPC. Press 'q' to quit.")
    
    # 1. Bật Camera
    stream = WebcamStream(src=0).start()
    
    # 2. Bật kết nối mạng gRPC
    worker = GrpcWorker(target='localhost:50051').start()

    # 3. Luồng hiển thị đồ họa
    while True:
        ret, frame = stream.read()
        if not ret or frame is None:
            continue

        # Đẩy ảnh vào Client gRPC
        worker.set_frame(frame)
        
        # Nhận tọa độ trả về từ Server gRPC
        boxes = worker.get_results()

        # Vẽ lên khung hình
        if boxes is not None:
            for box in boxes:
                label = f"{box.label} {box.confidence:.2f}"
                cv2.rectangle(frame, (box.x1, box.y1), (box.x2, box.y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (box.x1, box.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Sign Language YOLO (gRPC Ingestion Client)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    stream.stop()
    worker.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
