import RPi.GPIO as GPIO
import time
import threading

# Define GPIO pins for the Pan motor
PAN_DIR_PIN = 21  # DIR+
PAN_STEP_PIN = 13  # PUL+

# Define GPIO pins for limit switches
LIMIT_SWITCH_1_PIN = 20  # Replace with your actual GPIO pin number
LIMIT_SWITCH_2_PIN = 16  # Replace with your actual GPIO pin number

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(PAN_DIR_PIN, GPIO.OUT)
GPIO.setup(PAN_STEP_PIN, GPIO.OUT)
GPIO.setup(LIMIT_SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LIMIT_SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set initial direction for pan motor (Clockwise or Counterclockwise)
current_direction = GPIO.HIGH
GPIO.output(PAN_DIR_PIN, current_direction)

# Duration for motor to run continuously when switches are untouched
#run_duration = 5  # seconds

# Function to control the pan motor
def run_pan_motor():
    while GPIO.input(LIMIT_SWITCH_1_PIN) == GPIO.HIGH and GPIO.input(LIMIT_SWITCH_2_PIN) == GPIO.HIGH:
        GPIO.output(PAN_STEP_PIN, GPIO.HIGH)
        time.sleep(0.0010)  # Adjust step pulse duration as needed
        GPIO.output(PAN_STEP_PIN, GPIO.LOW)
        time.sleep(0.0010)

# Function to reverse motor direction
def reverse_motor_direction():
    global current_direction
    current_direction = GPIO.LOW if current_direction == GPIO.HIGH else GPIO.HIGH
    GPIO.output(PAN_DIR_PIN, current_direction)
    print("Motor direction reversed")

# Run the pan motor in a thread
try:
    while True:
        # Check if limit switches are untouched
        if GPIO.input(LIMIT_SWITCH_1_PIN) == GPIO.HIGH and GPIO.input(LIMIT_SWITCH_2_PIN) == GPIO.HIGH:
            # Start the pan motor thread if both switches are untouched
            pan_thread = threading.Thread(target=run_pan_motor)
            pan_thread.start()
            
            # Wait for the motor to run for the specified duration
            #time.sleep(run_duration)
            
            # Stop the motor thread after the duration
            pan_thread.join()
        else:
            # If a limit switch is touched, stop the motor and reverse direction
            print("Limit switch activated; reversing motor direction")
            reverse_motor_direction()
            time.sleep(0.5)  # Adjust delay as needed

except KeyboardInterrupt:
    print("Program terminated by User")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()
