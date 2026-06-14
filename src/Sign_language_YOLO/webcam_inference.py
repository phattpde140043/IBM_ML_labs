import cv2
from ultralytics import YOLO
import sys

def main():
    """
    Main function to run real-time YOLO inference using a webcam.
    """
    # 1. Load the YOLO model
    model_path = "best.pt"
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error loading model from {model_path}: {e}")
        sys.exit(1)

    # 2. Initialize the webcam (0 is typically the default built-in camera)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)

    print("Starting webcam inference. Press 'q' to quit.")

    # 3. Main inference loop
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Run YOLO inference on the frame
        # conf=0.5: Confidence threshold
        # verbose=False: Suppress console output for every frame to avoid log spam
        results = model(frame, conf=0.5, verbose=False)

        # Plot the predictions on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("Sign Language YOLO Inference", annotated_frame)

        # 4. Check for 'q' key to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    # 5. Graceful Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
