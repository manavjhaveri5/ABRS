import cv2
import numpy as np
from flask import Flask, Response

# Flask setup
app = Flask(__name__)

# Video setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device")
    exit()

# Set lower resolution for processing load
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# HSV color thresholding values for red
hueLow, hueHigh = 168, 179
satLow, satHigh = 101, 255
valLow, valHigh = 45, 255
min_contour_area = 500

def generate_frames():
    while True:
        success, frame = cap.read()
        if success:
            # Convert to HSV and create mask
            frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lowerBound = np.array([hueLow, satLow, valLow])
            upperBound = np.array([hueHigh, satHigh, valHigh])
            mask = cv2.inRange(frameHSV, lowerBound, upperBound)

            # Find contours and largest contour
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)

                if area > min_contour_area:
                    # Draw bounding box
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                    # Calculate and print centroid
                    center_x, center_y = x + w // 2, y + h // 2
                    print(f"Centroid: ({center_x}, {center_y})")

                    # Draw centroid point
                    cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)

            # Overlay mask onto frame for display
            mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            combined = cv2.hconcat([frame, mask_rgb])

            # Encode the frame for streaming
            ret, buffer = cv2.imencode('.jpg', combined)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
