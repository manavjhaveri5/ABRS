import os
import pygame
import sys
import time

# Set display environment variable for running Pygame on the Pi's screen
os.environ["DISPLAY"] = ":0"

# Initialize pygame
pygame.init()

# Set up the display (e.g., 480x320 for a Waveshare 3.5-inch LCD)
screen = pygame.display.set_mode((480, 320), pygame.FULLSCREEN)

# Background color and text properties
black = (0, 0, 0)
white = (255, 255, 255)
screen.fill(black)

colors = [
    (255, 0, 0),    # Red for "Chest Pass"
    (0, 100, 0),    # Green
    (0, 0, 255),    # Blue
    (200, 200, 0),  # Yellow for "Random Mode"
    (255, 165, 0)   # Orange for "Reset"
]

font = pygame.font.Font(pygame.font.match_font('arial'), 17)

# Define rectangles for button layout
rectangles = [
    pygame.Rect(20, 20, 120, 100),  # "Chest Pass"
    pygame.Rect(170, 20, 120, 100), # "Overhead Pass"
    pygame.Rect(320, 20, 120, 100), # "Bounce Pass"
    pygame.Rect(60, 180, 160, 100), # "Random Mode"
    pygame.Rect(260, 180, 160, 100) # "Reset"
]

rectangle_names = [
    'Chest Pass',
    'Overhead Pass',
    'Bounce Pass',
    'Random Mode',
    'Reset'
]

corner_radius = 5
selected_button = None

def draw_buttons():
    """Draws the interactive buttons on the screen."""
    for i, rect in enumerate(rectangles):
        pygame.draw.rect(screen, colors[i], rect, corner_radius)
        placeholder_text = font.render(rectangle_names[i], True, white)
        text_rect = placeholder_text.get_rect(center=rect.center)
        screen.blit(placeholder_text, text_rect)

# Draw initial buttons and update the display
draw_buttons()
pygame.display.update()

def display_message(message, color=(255, 255, 255), duration=3):
    """Displays a temporary message on the screen."""
    font = pygame.font.Font(pygame.font.match_font('arial'), 24)
    screen.fill(black)
    message_text = font.render(message, True, color)
    message_rect = message_text.get_rect(center=(240, 160))
    screen.blit(message_text, message_rect)
    pygame.display.update()
    time.sleep(duration)

def countdown_display(start=5):
    """Displays a countdown from the specified start value down to 1."""
    font = pygame.font.Font(pygame.font.match_font('arial'), 24)
    for i in range(start, 0, -1):
        screen.fill(black)
        countdown_text = font.render(f"Chest Pass selected. Turret starting in {i}...", True, white)
        countdown_text_rect = countdown_text.get_rect(center=(240, 160))
        screen.blit(countdown_text, countdown_text_rect)
        pygame.display.update()
        time.sleep(1)

def start_io_system():
    """Handles the user interaction for the touchscreen interface."""
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for i, rect in enumerate(rectangles):
                    if rect.collidepoint(mouse_pos):
                        selected_button = i + 1
                        print(f"Button {rectangle_names[i]} pressed, outputting state {selected_button}")
                        
                        # Display message on the screen
                        display_message(f"{rectangle_names[i]} selected", color=white if i == 0 else colors[i])

                        if i == 0:  # "Chest Pass" selected
                            countdown_display(5)  # Display countdown before starting
                            return 'Chest Pass'
                        elif i == 4:  # "Reset" button selected
                            display_message('Resetting...', color=(255, 0, 0))
                            return 'Reset'

        # Redraw buttons to maintain visual state
        screen.fill(black)
        draw_buttons()
        pygame.display.update()

    pygame.quit()
    sys.exit()

def display_stop_screen():
    """Displays a fullscreen Pygame window with a stop button and step information."""
    # No need to quit pygame, just continue with the existing pygame session
    stop_screen = pygame.display.set_mode((480, 320), pygame.FULLSCREEN)
    stop_screen.fill((0, 0, 0))  # Fill the screen with black
    font = pygame.font.Font(pygame.font.match_font('arial'), 24)

    # Stop button properties
    stop_button_radius = 60
    stop_button_center = (240, 160)
    red = (255, 0, 0)
    white = (255, 255, 255)

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Check if the stop button was clicked
                if ((mouse_pos[0] - stop_button_center[0]) ** 2 + (mouse_pos[1] - stop_button_center[1]) ** 2) ** 0.5 < stop_button_radius:
                    print("Stop button pressed")
                    running = False

        # Draw the stop button
        stop_screen.fill((0, 0, 0))  # Clear screen each frame
        pygame.draw.circle(stop_screen, red, stop_button_center, stop_button_radius)
        stop_text = font.render("STOP", True, white)
        stop_text_rect = stop_text.get_rect(center=stop_button_center)
        stop_screen.blit(stop_text, stop_text_rect)

        # Example step size text (can be updated with actual values during the main loop)
        step_size_text = font.render("Step Size: 0", True, white)
        step_size_rect = step_size_text.get_rect(center=(240, 280))
        stop_screen.blit(step_size_text, step_size_rect)

        # Update the display
        pygame.display.update()

    pygame.quit()
    sys.exit()