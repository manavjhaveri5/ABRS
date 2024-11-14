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
run_duration = 5  # seconds

# Function to control the pan motor
def run_pan_motor():
    while True:
        GPIO.output(PAN_STEP_PIN, GPIO.HIGH)
        time.sleep(0.0010)  # Adjust step pulse duration as needed
        GPIO.output(PAN_STEP_PIN, GPIO.LOW)
        time.sleep(0.0010)

# Function to reverse motor direction and restart after a delay
def reverse_and_restart_motor():
    global current_direction
    # Reverse direction
    current_direction = GPIO.LOW if current_direction == GPIO.HIGH else GPIO.HIGH
    GPIO.output(PAN_DIR_PIN, current_direction)
    print("Motor direction reversed")
    
    # Wait 1 second before restarting
    time.sleep(1)
    
    # Restart the motor in the new direction
    motor_thread = threading.Thread(target=run_pan_motor)
    motor_thread.start()
    return motor_thread

# Run the pan motor in a thread
try:
    # Start the initial motor thread
    motor_thread = threading.Thread(target=run_pan_motor)
    motor_thread.start()

    while True:
        # Check limit switches
        if GPIO.input(LIMIT_SWITCH_1_PIN) == GPIO.LOW or GPIO.input(LIMIT_SWITCH_2_PIN) == GPIO.LOW:
            print("Limit switch activated; stopping motor and reversing direction")
            
            # Stop the current motor thread
            motor_thread.join()
            
            # Reverse direction and restart after delay
            motor_thread = reverse_and_restart_motor()

        # Short delay to prevent constant polling
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Program terminated by User")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()
