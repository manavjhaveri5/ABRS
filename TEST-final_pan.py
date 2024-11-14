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

# GPIO setup for Pan Motor and Limit Switches
PAN_DIR_PIN = 21    # Direction pin
PAN_STEP_PIN = 13  # Step pin
LIMIT_SWITCH_1_PIN = 20  # Replace with your actual GPIO pin number
LIMIT_SWITCH_2_PIN = 16  # Replace with your actual GPIO pin number
GPIO.setmode(GPIO.BCM)
GPIO.setup(PAN_DIR_PIN, GPIO.OUT)
GPIO.setup(PAN_STEP_PIN, GPIO.OUT)
GPIO.setup(LIMIT_SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LIMIT_SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Motor control variables
current_direction = GPIO.HIGH  # Initial direction for the motor
GPIO.output(PAN_DIR_PIN, current_direction)
movement_threshold = 10  # Threshold to detect significant movement
previous_center_x = None  # For tracking the previous position of the object
run_duration = 0.1  # Duration for motor movement in seconds

# Global variable to control motor state
running = False
motor_thread = None

# Function to control the pan motor
def run_pan_motor():
    while running:
        GPIO.output(PAN_STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Adjust step pulse duration as needed
        GPIO.output(PAN_STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

# Function to start motor in a specific direction
def start_motor(direction):
    global running, motor_thread, current_direction
    GPIO.output(PAN_DIR_PIN, direction)
    current_direction = direction
    if not running:
        running = True
        motor_thread = threading.Thread(target=run_pan_motor)
        motor_thread.start()

# Function to stop the motor
def stop_motor():
    global running, motor_thread
    if running:
        running = False
        if motor_thread:
            motor_thread.join()

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

                    # Determine direction based on movement (reverse logic)
                    if previous_center_x is not None:
                        movement = center_x - previous_center_x
                        if movement > movement_threshold:
                            print("Moving left")
                            start_motor(GPIO.LOW)  # Move left when object moves right
                        elif movement < -movement_threshold:
                            print("Moving right")
                            start_motor(GPIO.HIGH)  # Move right when object moves left
                        else:
                            stop_motor()  # Stop motor if no significant movement
                    
                    # Update the previous center_x position
                    previous_center_x = center_x
                else:
                    stop_motor()  # Stop motor if contour area is too small
            else:
                stop_motor()  # Stop motor if no contours found

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
        # Run the Flask app in a separate thread
        flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080})
        flask_thread.start()

        while True:
            # Check if a limit switch is pressed
            if GPIO.input(LIMIT_SWITCH_1_PIN) == GPIO.LOW or GPIO.input(LIMIT_SWITCH_2_PIN) == GPIO.LOW:
                print("Limit switch activated; stopping motor and reversing direction")
                stop_motor()
                current_direction = GPIO.LOW if current_direction == GPIO.HIGH else GPIO.HIGH
                GPIO.output(PAN_DIR_PIN, current_direction)
                time.sleep(1)  # Delay before restarting in the opposite direction

            # Short delay to prevent constant polling
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Program terminated by User")

    finally:
        # Ensure the motor stops and GPIO is cleaned up
        stop_motor()
        cap.release()
        GPIO.cleanup()
