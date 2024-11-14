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
LIMIT_SWITCH_1_PIN = 20  # Replace with your actual GPIO pin number (left switch)
LIMIT_SWITCH_2_PIN = 16  # Replace with your actual GPIO pin number (right switch)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PAN_DIR_PIN, GPIO.OUT)
GPIO.setup(PAN_STEP_PIN, GPIO.OUT)
GPIO.setup(LIMIT_SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LIMIT_SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Motor control variables
current_direction = GPIO.HIGH  # Initial direction for the motor
GPIO.output(PAN_DIR_PIN, current_direction)
center_x_target = 150  # Target x-coordinate for the centroid
center_tolerance = 20  # Allowable tolerance around the center_x_target
running = False
motor_thread = None
resetting = False  # Flag to indicate if the motor is resetting to center

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
    if not resetting:  # Only allow movement if not resetting
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

# Function to reset motor to center when hitting a limit switch
def reset_to_center(direction, duration=2.5):
    global resetting
    resetting = True
    stop_motor()  # Stop any ongoing motor movement
    GPIO.output(PAN_DIR_PIN, direction)
    start_time = time.time()
    while time.time() - start_time < duration:
        GPIO.output(PAN_STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(PAN_STEP_PIN, GPIO.LOW)
        time.sleep(0.001)
    resetting = False  # Reset complete

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

                if area > min_contour_area and not resetting:  # Only track if not resetting
                    # Draw bounding box and centroid
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    center_x = x + w // 2
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.circle(frame, (center_x, y + h // 2), 5, (0, 255, 0), -1)

                    # Adjust motor based on center_x position
                    if center_x < center_x_target - center_tolerance:
                        print("Moving left to center")
                        start_motor(GPIO.LOW)  # Move left to center
                    elif center_x > center_x_target + center_tolerance:
                        print("Moving right to center")
                        start_motor(GPIO.HIGH)  # Move right to center
                    else:
                        print("Centered; motor stopped")
                        stop_motor()  # Stop motor if within tolerance range
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
            if GPIO.input(LIMIT_SWITCH_1_PIN) == GPIO.LOW:
                print("Left limit switch activated; resetting to center")
                reset_to_center(GPIO.HIGH, 2)  # Move clockwise for 2.5 seconds
            elif GPIO.input(LIMIT_SWITCH_2_PIN) == GPIO.LOW:
                print("Right limit switch activated; resetting to center")
                reset_to_center(GPIO.LOW, 2)  # Move counterclockwise for 2.5 seconds

            # Short delay to prevent constant polling
            time.sleep(1)

    except KeyboardInterrupt:
        print("Program terminated by User")

    finally:
        # Ensure the motor stops and GPIO is cleaned up
        stop_motor()
        cap.release()
        GPIO.cleanup()
