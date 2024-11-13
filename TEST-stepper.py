import RPi.GPIO as GPIO
import time
import threading

# Define GPIO pins for the Pan motor
PAN_DIR_PIN = 5  # DIR+
PAN_STEP_PIN = 12  # PUL+

# Define GPIO pins for the Tilt motor
TILT_DIR_PIN = 21  # DIR+
TILT_STEP_PIN = 13  # PUL+

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(PAN_DIR_PIN, GPIO.OUT)
GPIO.setup(PAN_STEP_PIN, GPIO.OUT)
GPIO.setup(TILT_DIR_PIN, GPIO.OUT)
GPIO.setup(TILT_STEP_PIN, GPIO.OUT)

# Set directions for both motors (Clockwise or Counterclockwise)
GPIO.output(PAN_DIR_PIN, GPIO.HIGH)  # HIGH for one direction, LOW for the opposite
GPIO.output(TILT_DIR_PIN, GPIO.HIGH)  # HIGH for one direction, LOW for the opposite

# Set duration for motors to run
run_duration = 10  # in seconds

# Function to control pan motor
def run_pan_motor():
    start_time = time.time()
    while time.time() - start_time < run_duration:
        GPIO.output(PAN_STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Adjust step pulse duration as needed
        GPIO.output(PAN_STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

# Function to control tilt motor
def run_tilt_motor():
    start_time = time.time()
    while time.time() - start_time < run_duration:
        GPIO.output(TILT_STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Adjust step pulse duration as needed
        GPIO.output(TILT_STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

# Run both motors simultaneously using threading
try:
    pan_thread = threading.Thread(target=run_pan_motor)
    tilt_thread = threading.Thread(target=run_tilt_motor)
    
    # Start both threads
    pan_thread.start()
    tilt_thread.start()
    
    # Wait for both threads to complete
    pan_thread.join()
    tilt_thread.join()

except KeyboardInterrupt:
    print("Stopped by User")
finally:
    # Clean up GPIO settings
    GPIO.cleanup()
