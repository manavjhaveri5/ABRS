import RPi.GPIO as GPIO
import time

# Define GPIO pins for the limit switches
LIMIT_SWITCH_1 = 26  # Replace with your actual GPIO pin
LIMIT_SWITCH_2 = 19  # Replace with your actual GPIO pin

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)

# Setup limit switches as inputs with internal pull-up resistors
GPIO.setup(LIMIT_SWITCH_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LIMIT_SWITCH_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("Press the limit switches to test their functionality.")
    while True:
        # Read the state of each limit switch
        switch1_state = GPIO.input(LIMIT_SWITCH_1)
        switch2_state = GPIO.input(LIMIT_SWITCH_2)

        # Print switch status; the input will be LOW (False) when pressed
        if switch1_state == GPIO.LOW:
            print("Limit Switch 1 Pressed")
        if switch2_state == GPIO.LOW:
            print("Limit Switch 2 Pressed")
        
        # Small delay to debounce
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting program")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()
