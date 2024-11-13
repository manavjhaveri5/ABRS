"""
This Raspberry Pi code was developed by newbiely.com
This Raspberry Pi code is made available for public use without any restriction.
For comprehensive instructions and wiring diagrams, please visit:
https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-limit-switch
"""

import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for your button
SWITCH_PIN = 26  # or 19 for SWITCH 1

# Define debounce time in milliseconds
DEBOUNCE_TIME_MS = 300  # Increase debounce to 300 milliseconds

# Set the initial state and pull-up resistor for the button
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the button state and previous state
switch_state = GPIO.input(SWITCH_PIN)
prev_switch_state = switch_state

# Define a function to handle button presses
def button_callback(channel):
    global switch_state
    switch_state = GPIO.input(SWITCH_PIN)
    print(f"Callback triggered, current switch state: {'UNTOUCHED' if switch_state == GPIO.HIGH else 'TOUCHED'}")

# Add an event listener for the button press
GPIO.add_event_detect(SWITCH_PIN, GPIO.BOTH, callback=button_callback, bouncetime=DEBOUNCE_TIME_MS)

try:
    # Main loop
    while True:
        # Check if the button state has changed
        if switch_state != prev_switch_state:
            if switch_state == GPIO.HIGH:
                print("The limit switch: TOUCHED -> UNTOUCHED")
            else:
                print("The limit switch: UNTOUCHED -> TOUCHED")
            
            prev_switch_state = switch_state

        # Small delay in main loop to avoid flooding the terminal
        time.sleep(0.2)

except KeyboardInterrupt:
    # Clean up GPIO on exit
    GPIO.cleanup()
