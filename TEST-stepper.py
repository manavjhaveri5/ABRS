import RPi.GPIO as GPIO
import time

# Define GPIO pins
DIR_PIN = 5  # DIR+
STEP_PIN = 12  # PUL+

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

# Set the direction (Clockwise or Counterclockwise)
GPIO.output(DIR_PIN, GPIO.HIGH)  # HIGH for one direction, LOW for the opposite

# Set duration for motor run
run_duration = 10  # in seconds
start_time = time.time()

try:
    while time.time() - start_time < run_duration:
        # Perform one step
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Adjusted to 1000 microseconds
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.001)  # Adjusted to 1000 microseconds
except KeyboardInterrupt:
    print("Stopped by User")
finally:
    # Clean up the GPIO settings
    GPIO.cleanup()
