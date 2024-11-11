import RPi.GPIO as GPIO
import time

# GPIO setup
DIR_PIN = 21       # GPIO pin for direction
STEP_PIN = 20      # GPIO pin for stepping

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

def test_motor(step_delay):
    # Rotate right
    GPIO.output(DIR_PIN, GPIO.HIGH)
    for _ in range(200):  # Adjust 200 to fit the desired rotation steps
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)
    time.sleep(1)

    # Rotate left
    GPIO.output(DIR_PIN, GPIO.LOW)
    for _ in range(200):  # Adjust 200 to fit the desired rotation steps
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)
    time.sleep(1)

try:
    # Simple test loop
    print("Testing motor...")
    for _ in range(5):  # Loop 5 times for testing
        test_motor(step_delay=0.01)

finally:
    # Clean up GPIO pins
    GPIO.cleanup()
    print("GPIO cleanup complete.")
