import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import threading
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

# GPIO setup for Pan Motor
PAN_DIR_PIN = 13    # Direction pin
PAN_STEP_PIN = 21  # Step pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(PAN_DIR_PIN, GPIO.OUT)
GPIO.setup(PAN_STEP_PIN, GPIO.OUT)

# Pan motor parameters
movement_threshold = 10  # Threshold to detect significant movement
previous_center_x = None  # For tracking the previous position of the object
run_duration = 0.1  # Duration for motor movement in seconds

# Define pan motor control functions
def move_motor_left():
    GPIO.output(PAN_DIR_PIN, GPIO.LOW)  # Set direction to left
    pulse_motor()

def move_motor_right():
    GPIO.output(PAN_DIR_PIN, GPIO.HIGH)  # Set direction to right
    pulse_motor()

def pulse_motor():
    start_time = time.time()
    while time.time() - start_time < run_duration:
        GPIO.output(PAN_STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Pulse duration; adjust for speed
        GPIO.output(PAN_STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

# Function to process frames and detect movement
def generate_frames():
    global previous_center_x
    while True:
        success, frame = cap.read()
        if success:
            # Convert to HSV and create mask
            frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lowerBound = np.array([hueLow, satLow, valLow])
            upperBound = np.array([hueHigh, satHigh, valHigh])
            mask = cv2.inRange(frameHSV, lowerBound, upperBound)

            # Find contours and select the largest one
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)

                if area > min_contour_area:
                    # Draw bounding box and centroid
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    center_x = x + w // 2
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.circle(frame, (center_x, y + h // 2), 5, (0, 255, 0), -1)

                    # Determine direction based on movement
                    if previous_center_x is not None:
                        movement = center_x - previous_center_x
                        if movement > movement_threshold:
                            threading.Thread(target=move_motor_right).start()
                        elif movement < -movement_threshold:
                            threading.Thread(target=move_motor_left).start()
                    
                    # Update the previous center_x position
                    previous_center_x = center_x

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

# Main entry point
if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("Application interrupted by the user")
    finally:
        cap.release()
        GPIO.cleanup()
