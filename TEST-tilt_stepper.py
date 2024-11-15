import RPi.GPIO as GPIO
import time

# Define GPIO pins for the tilt motor
TILT_DIR_PIN = 5  # DIR+
TILT_STEP_PIN = 12  # PUL+

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(TILT_DIR_PIN, GPIO.OUT)
GPIO.setup(TILT_STEP_PIN, GPIO.OUT)

# Function to move motor forward and backward
def move_motor(forward_time, backward_time):
    # Move forward
    start_time = time.time()
    while time.time() - start_time < forward_time:
        GPIO.output(TILT_STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Adjust step pulse duration as needed
        GPIO.output(TILT_STEP_PIN, GPIO.LOW)
        time.sleep(0.001)
    
    # Move backward
    GPIO.output(TILT_DIR_PIN, GPIO.LOW)  # Reverse direction
    start_time = time.time()
    while time.time() - start_time < backward_time:
        GPIO.output(TILT_STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Adjust step pulse duration as needed
        GPIO.output(TILT_STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

# Main logic to get user input and move the motor accordingly
try:
    while True:
        # Get user input for movement choice
        user_input = input("Enter choice (c for 2s forward/back, o for 3s forward/back, d for 4s forward/back): ").lower()

        if user_input == 'c':
            print("Moving 2 seconds forward and 2 seconds back.")
            move_motor(2, 2)
        elif user_input == 'o':
            print("Moving 3 seconds forward and 3 seconds back.")
            move_motor(3, 3)
        elif user_input == 'd':
            print("Moving 4 seconds forward and 4 seconds back.")
            move_motor(4, 4)
        else:
            print("Invalid input, please enter 'c', 'o', or 'd'.")
        
except KeyboardInterrupt:
    print("Program terminated by User")

finally:
    # Cleanup GPIO pins
    GPIO.cleanup()
