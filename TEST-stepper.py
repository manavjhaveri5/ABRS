import RPi.GPIO as GPIO
import time

# GPIO setup
DIR_PIN = 21       # GPIO pin for direction
STEP_PIN = 20      # GPIO pin for stepping

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

def run_motor(direction, run_time, step_delay):
    # Set direction: 'R' for right, 'L' for left
    GPIO.output(DIR_PIN, GPIO.HIGH if direction == 'R' else GPIO.LOW)
    
    start_time = time.time()
    while time.time() - start_time < run_time:
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)

try:
    # Run motor to the right for 10 seconds
    print("Running motor to the right for 10 seconds...")
    run_motor(direction='R', run_time=10, step_delay=0.01)
    time.sleep(1)
    
    # Run motor to the left for 10 seconds
    print("Running motor to the left for 10 seconds...")
    run_motor(direction='L', run_time=10, step_delay=0.01)

finally:
    # Clean up GPIO pins
    GPIO.cleanup()
    print("GPIO cleanup complete.")
