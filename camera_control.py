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
step_size = 0

def process_video():
    global current_frame, stop_panning, step_size
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
    """Displays a Pygame window with a Stop button during camera control, along with the step size."""
    global stop_panning, step_size
    pygame.init()
    screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
    pygame.display.set_caption('Camera Control')
    clock = pygame.time.Clock()

    # Colors
    background_color = (30, 30, 30)  # Dark grey background
    button_color = (255, 0, 0)  # Red color for stop button
    button_hover_color = (200, 0, 0)  # Darker red for hover
    text_color = (255, 255, 255)  # White for text
    step_size_color = (0, 255, 0)  # Green for step size text

    # Fonts
    font = pygame.font.Font(pygame.font.match_font('arial'), 24)

    # Stop button properties
    button_radius = 60
    button_center = (540, 80)  # x, y coordinates for button center

    running = True
    while running:
        screen.fill(background_color)  # Fill screen with background color

        # Draw stop button
        mouse_pos = pygame.mouse.get_pos()
        button_color_to_use = button_hover_color if (mouse_pos[0] - button_center[0]) ** 2 + (mouse_pos[1] - button_center[1]) ** 2 < button_radius ** 2 else button_color
        pygame.draw.circle(screen, button_color_to_use, button_center, button_radius)

        # Draw stop text on button
        stop_text = font.render('Stop', True, text_color)
        stop_text_rect = stop_text.get_rect(center=button_center)
        screen.blit(stop_text, stop_text_rect)

        # Display step size on the screen
        step_size_text = font.render(f'Step Size: {step_size}', True, step_size_color)
        step_size_rect = step_size_text.get_rect(center=(320, 240))
        screen.blit(step_size_text, step_size_rect)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                stop_panning = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (mouse_pos[0] - button_center[0]) ** 2 + (mouse_pos[1] - button_center[1]) ** 2 < button_radius ** 2:
                    print("Stop button clicked, exiting...")
                    running = False
                    stop_panning = True

        pygame.display.update()
        clock.tick(30)  # Limit the frame rate to 30 FPS

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
