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

font = pygame.font.Font(pygame.font.match_font('arial'), 18)

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

                        # Start the corresponding phase
                        if i == 0:  # "Chest Pass" selected
                            print("Starting Chest Pass phase...")

                            # Flash "Starting Chest Pass Phase" message
                            flash_font = pygame.font.Font(pygame.font.match_font('arial'), 20)
                            for _ in range(3):  # Flashing 3 times
                                screen.fill(black)
                                flash_text = flash_font.render('Starting Chest Pass Phase...', True, (255, 0, 0))
                                flash_text_rect = flash_text.get_rect(center=(240, 160))
                                screen.blit(flash_text, flash_text_rect)
                                pygame.display.update()
                                time.sleep(0.5)
                                screen.fill(black)
                                pygame.display.update()
                                time.sleep(0.5)

                            pygame.quit()  # Quit Pygame after showing the message
                            return 'Chest Pass'  # Return to main for the next action

                        elif i == 4:  # "Reset" button selected
                            # Flash "Resetting..." message
                            reset_font = pygame.font.Font(pygame.font.match_font('arial'), 24)
                            for _ in range(5):
                                screen.fill(black)
                                reset_text = reset_font.render('Resetting...', True, (255, 0, 0))
                                reset_text_rect = reset_text.get_rect(center=(240, 160))
                                screen.blit(reset_text, reset_text_rect)
                                pygame.display.update()
                                time.sleep(0.5)
                                screen.fill(black)
                                pygame.display.update()
                                time.sleep(0.5)

                            return 'Reset'  # Return to main indicating reset

        # Redraw buttons to maintain visual state
        screen.fill(black)
        draw_buttons()
        pygame.display.update()

    # Quit pygame when the main loop ends
    pygame.quit()
    sys.exit()
