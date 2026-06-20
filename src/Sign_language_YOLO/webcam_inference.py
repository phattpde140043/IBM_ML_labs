import cv2
import threading
import sys
from ultralytics import YOLO

class WebcamStream:
    """Thread 1: Đọc ảnh liên tục từ Webcam (Producer)"""
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            sys.exit(1)
        self.ret, self.frame = self.cap.read()
        if self.ret:
            self.frame = cv2.flip(self.frame, 1) # Mirror effect
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
                frame = cv2.flip(frame, 1) # Lật ảnh ngang liên tục
                with self.lock:
                    self.ret = ret
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy()

    def stop(self):
        self.stopped = True
        self.cap.release()

class InferenceWorker:
    """Thread 2: Xử lý AI Inference (Worker)"""
    def __init__(self, model_path="best.pt"):
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading model from {model_path}: {e}")
            sys.exit(1)
        
        self.frame_to_process = None
        self.latest_boxes = None
        self.stopped = False
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()
        return self

    def set_frame(self, frame):
        """Main Thread sẽ gọi hàm này để gửi ảnh cho AI"""
        with self.cond:
            self.frame_to_process = frame
            self.cond.notify() # Đánh thức worker dậy để làm việc

    def get_results(self):
        """Main Thread sẽ gọi hàm này để lấy kết quả mới nhất"""
        with self.lock:
            return self.latest_boxes

    def run(self):
        """Vòng lặp ngầm của AI"""
        while not self.stopped:
            with self.cond:
                # Ngủ chờ cho đến khi có ảnh mới hoặc bị dừng
                self.cond.wait_for(lambda: self.frame_to_process is not None or self.stopped)
                if self.stopped:
                    break
                frame = self.frame_to_process
                self.frame_to_process = None
            
            if frame is not None:
                # Chạy YOLO inference
                results = self.model(frame, conf=0.5, verbose=False)
                # Lưu tọa độ Bounding Box vào biến dùng chung
                with self.lock:
                    self.latest_boxes = results[0].boxes.cpu().numpy() if results[0].boxes else None

    def stop(self):
        with self.cond:
            self.stopped = True
            self.cond.notify()

def main():
    """Thread 3: Hiển thị mượt mà (Consumer / Main Thread)"""
    print("Starting 3-Thread webcam inference. Press 'q' to quit.")

    # 1. Khởi động Camera Thread
    stream = WebcamStream(src=0).start()

    # 2. Khởi động AI Thread
    worker = InferenceWorker(model_path="best.pt").start()

    while True:
        # Lấy ảnh siêu mượt từ Camera (FPS cao)
        ret, frame = stream.read()
        if not ret or frame is None:
            continue

        # Gửi ảnh này cho AI phân tích ngầm (không đợi kết quả)
        worker.set_frame(frame)

        # Lấy kết quả Bounding Box GẦN NHẤT từ AI (có thể là kết quả của ảnh trước đó)
        boxes = worker.get_results()

        # Vẽ đè Bounding Box lên bức ảnh siêu mượt
        if boxes is not None:
            for box in boxes:
                b = box.xyxy[0].astype(int) # Tọa độ [x1, y1, x2, y2]
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = f"{worker.model.names[cls]} {conf:.2f}"
                
                # Vẽ HCN
                cv2.rectangle(frame, (b[0], b[1]), (b[2], b[3]), (0, 255, 0), 2)
                # In chữ
                cv2.putText(frame, label, (b[0], b[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Hiển thị ra màn hình (30-60 FPS)
        cv2.imshow("Sign Language YOLO Inference (3-Thread Ultra-Smooth)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    # Dọn dẹp
    stream.stop()
    worker.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
