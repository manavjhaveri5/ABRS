import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
from flask import Flask, Response
import threading
import pygame

# GPIO setup
DIR_PIN = 20  # GPIO pin for direction
STEP_PIN = 21  # GPIO pin for stepping

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    GPIO.setup(STEP_PIN, GPIO.OUT)

# Flask setup
app = Flask(__name__)

# Video setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device")
    GPIO.cleanup()
    exit()

# Set lower resolution to reduce processing load
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set resolution width to a bigger size
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set resolution height to a bigger size
cap.set(cv2.CAP_PROP_FPS, 10)  # Lower the frame rate to reduce lag

# HSV color thresholding values for red
hueLow, hueHigh = 170, 180
satLow, satHigh = 70, 255
valLow, valHigh = 50, 255
min_contour_area = 500  # Minimum area to consider a contour for tracking

# Frame parameters
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_center_x = frame_width // 2  # Center x-coordinate of the frame

# Proportional control gain for mapping offset to motor steps
K_p = 0.05  # Adjust this value to control sensitivity

# Global variable for the current frame to be used in streaming
current_frame = None

# Flag for stopping the panning process
stop_panning = False

def move_stepper(step_size, direction):
    if stop_panning:  # Check if the stop button was pressed
        return
    GPIO.output(DIR_PIN, GPIO.HIGH if direction == 'R' else GPIO.LOW)
    for _ in range(step_size):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

# Function to process frames and control the stepper motor
def process_video():
    global current_frame, stop_panning
    while cap.isOpened() and not stop_panning:
        success, frame = cap.read()

        if success:
            frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lowerBound = np.array([hueLow, satLow, valLow])
            upperBound = np.array([hueHigh, satHigh, valHigh])
            myMask = cv2.inRange(frameHSV, lowerBound, upperBound)

            contours, _ = cv2.findContours(myMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)

                if area > min_contour_area:
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                    center_x = x + w // 2
                    offset_x = center_x - frame_center_x
                    print(f"Offset X: {offset_x}")

                    step_size = int(K_p * abs(offset_x))

                    if abs(offset_x) > 20:
                        if offset_x > 0:
                            move_stepper(step_size, 'R')
                        else:
                            move_stepper(step_size, 'L')

                    cv2.circle(frame, (center_x, y + h // 2), 5, (0, 255, 0), -1)

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 30])  # Lower quality to reduce latency
            if not ret:
                print("Error: Frame encoding failed")
            else:
                current_frame = buffer.tobytes()
        else:
            break

    stop_panning = False  # Reset flag after stopping

# Pygame function to add a stop button overlay
def display_stop_button():
    global stop_panning
    pygame.init()
    screen = pygame.display.set_mode((640, 480))  # Increase window size
    stop_button = pygame.Rect(540, 10, 80, 40)  # Adjust button position accordingly
    red = (255, 0, 0)
    white = (255, 255, 255)
    font = pygame.font.Font(pygame.font.match_font('arial'), 20)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                stop_panning = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if stop_button.collidepoint(event.pos):
                    print("Stop button clicked, exiting...")
                    running = False
                    stop_panning = True

        screen.fill((0, 0, 0))  # Black background
        pygame.draw.rect(screen, red, stop_button)
        stop_text = font.render('Stop', True, white)
        stop_text_rect = stop_text.get_rect(center=stop_button.center)
        screen.blit(stop_text, stop_text_rect)
        pygame.display.update()

    pygame.quit()

# Flask route to stream the video feed
@app.route('/video_feed')
def video_feed():
    print("Video feed accessed")
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Generator function to yield video frames
def gen():
    global current_frame
    time.sleep(2)  # Give time for initialization
    while not stop_panning:
        if current_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n\r\n')

def start_pan_control():
    setup_gpio()
    # Start the video processing in a separate thread
    video_thread = threading.Thread(target=process_video)
    video_thread.daemon = True
    video_thread.start()

    # Start the stop button overlay
    button_thread = threading.Thread(target=display_stop_button)
    button_thread.daemon = True
    button_thread.start()

    # Wait for both threads to finish
    video_thread.join()
    button_thread.join()

    cap.release()
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup_gpio()
        # Start the pan control in a separate thread
        control_thread = threading.Thread(target=start_pan_control)
        control_thread.daemon = True
        control_thread.start()

        # Start the Flask server
        app.run(host='0.0.0.0', port=8080, threaded=True)

    finally:
        cap.release()
        GPIO.cleanup()

# Verify the camera stream locally (for debugging purposes)
if __name__ == "__main__":
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Camera Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()
