import RPi.GPIO as GPIO
import time
import threading

# Define GPIO pins for the Pan motor
PAN_DIR_PIN = 21  # DIR+
PAN_STEP_PIN = 13  # PUL+

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(PAN_DIR_PIN, GPIO.OUT)
GPIO.setup(PAN_STEP_PIN, GPIO.OUT)

# Set direction for pan motor (Clockwise or Counterclockwise)
GPIO.output(PAN_DIR_PIN, GPIO.HIGH)  # Set to HIGH for one direction, LOW for the opposite

# Set duration for motor to run
run_duration = 3  # in seconds

# Function to control pan motor
def run_pan_motor():
    start_time = time.time()
    while time.time() - start_time < run_duration:
        GPIO.output(PAN_STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Adjust step pulse duration as needed
        GPIO.output(PAN_STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

# Run pan motor in a separate thread
try:
    pan_thread = threading.Thread(target=run_pan_motor)
    
    # Start the pan motor thread
    pan_thread.start()
    
    # Wait for the pan motor thread to complete
    pan_thread.join()

except KeyboardInterrupt:
    print("Stopped by User")
finally:
    # Clean up GPIO settings
    GPIO.cleanup()
