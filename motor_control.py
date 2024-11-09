import RPi.GPIO as GPIO
import time

# GPIO pin setup for motor control
DIR_PIN = 20  # GPIO pin for direction
STEP_PIN = 21  # GPIO pin for stepping

def setup_motor_gpio():
    """Initializes GPIO pins for the motor."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    GPIO.setup(STEP_PIN, GPIO.OUT)

def move_motor(step_size, direction):
    """
    Moves the stepper motor in the specified direction.
    
    Args:
        step_size (int): Number of steps to move.
        direction (str): 'R' for right, 'L' for left.
    """
    GPIO.output(DIR_PIN, GPIO.HIGH if direction == 'R' else GPIO.LOW)
    for _ in range(step_size):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

def cleanup_motor_gpio():
    """Cleans up GPIO pins."""
    GPIO.cleanup()
