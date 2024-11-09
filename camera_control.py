import cv2
import numpy as np
from flask import Flask, Response
import threading
import time
import pygame
from motor_control import setup_motor_gpio, move_motor, cleanup_motor_gpio

# Flask setup
app = Flask(__name__)

# Video setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device")
    cleanup_motor_gpio()
    exit()

# Set lower resolution for processing load
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 10)

# HSV color thresholding values for red
hueLow, hueHigh = 170, 180
satLow, satHigh = 70, 255
valLow, valHigh = 50, 255
min_contour_area = 500
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_center_x = frame_width // 2
K_p = 0.05

current_frame = None
stop_panning = False

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
                    center_x = x + w // 2
                    offset_x = center_x - frame_center_x
                    print(f"Offset X: {offset_x}")

                    step_size = int(K_p * abs(offset_x))
                    if abs(offset_x) > 20:
                        if offset_x > 0:
                            move_motor(step_size, 'R')
                        else:
                            move_motor(step_size, 'L')

                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.circle(frame, (center_x, y + h // 2), 5, (0, 255, 0), -1)

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
            if not ret:
                print("Error: Frame encoding failed")
            else:
                current_frame = buffer.tobytes()
        else:
            break

    stop_panning = False

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen():
    global current_frame
    time.sleep(2)
    while not stop_panning:
        if current_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n\r\n')

def display_stop_button():
    """Displays a Pygame window with a Stop button during camera control."""
    global stop_panning
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Stop Camera Control')
    stop_button = pygame.Rect(540, 10, 80, 40)
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

        # Draw stop button
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, red, stop_button)
        stop_text = font.render('Stop', True, white)
        stop_text_rect = stop_text.get_rect(center=stop_button.center)
        screen.blit(stop_text, stop_text_rect)
        pygame.display.update()

    pygame.quit()

def start_camera_control():
    setup_motor_gpio()
    # Start the video processing in a separate thread
    video_thread = threading.Thread(target=process_video)
    video_thread.daemon = True
    video_thread.start()

    # Start the stop button overlay in a separate thread
    button_thread = threading.Thread(target=display_stop_button)
    button_thread.daemon = True
    button_thread.start()

    # Wait for threads to finish
    video_thread.join()
    button_thread.join()

    cap.release()
    cleanup_motor_gpio()

if __name__ == "__main__":
    try:
        setup_motor_gpio()
        control_thread = threading.Thread(target=start_camera_control)
        control_thread.daemon = True
        control_thread.start()
        app.run(host='0.0.0.0', port=8080, threaded=True)
    finally:
        cap.release()
        cleanup_motor_gpio()
