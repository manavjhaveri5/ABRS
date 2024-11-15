import RPi.GPIO as GPIO
import time

# Define GPIO pins for the tilt motor
TILT_DIR_PIN = 5  # DIR+
TILT_STEP_PIN = 12  # PUL+

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(TILT_DIR_PIN, GPIO.OUT)
GPIO.setup(TILT_STEP_PIN, GPIO.OUT)

# Set initial direction for tilt motor (Clockwise or Counterclockwise)
GPIO.output(TILT_DIR_PIN, GPIO.HIGH)

# Run tilt motor for 3 seconds
start_time = time.time()
while time.time() - start_time < 3:  # Run for 3 seconds
    GPIO.output(TILT_STEP_PIN, GPIO.HIGH)
    time.sleep(0.001)  # Adjust step pulse duration as needed
    GPIO.output(TILT_STEP_PIN, GPIO.LOW)
    time.sleep(0.001)

# Cleanup GPIO pins after operation
GPIO.cleanup()
