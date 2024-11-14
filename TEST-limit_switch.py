import RPi.GPIO as GPIO
import time

# Define GPIO pins for limit switches
LIMIT_SWITCH_1_PIN = 20  # Replace with your actual GPIO pin number
LIMIT_SWITCH_2_PIN = 16  # Replace with your actual GPIO pin number

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIMIT_SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LIMIT_SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Check limit switch 1
        if GPIO.input(LIMIT_SWITCH_1_PIN) == GPIO.LOW:
            print("Limit Switch 1: Touched")
        elif GPIO.input(LIMIT_SWITCH_2_PIN) == GPIO.LOW:
            print("Limit Switch 2: Touched")
        
        time.sleep(0.5)  # Adjust delay as needed

except KeyboardInterrupt:
    print("Program terminated")

finally:
    GPIO.cleanup()
