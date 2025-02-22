import gpiozero
import pygame
import time
import json
import os
import sys

# Set up the GPIO pin for the button
button = gpiozero.Button(17, pull_up=True, bounce_time=0.1)

# Initialize pygame for image handling and sound playback
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
pygame.init()

# Set up the Pygame screen (full-screen mode)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Clue Box")

# Load background image using pygame
def load_background_image(image_path="bg.jpg"):
    try:
        bg_image = pygame.image.load(image_path)
        # Resize the image to fit the screen size
        bg_image = pygame.transform.scale(bg_image, (screen.get_width(), screen.get_height()))
        return bg_image
    except Exception as e:
        print(f"Error loading background image: {e}")
        return None

# Load the background image
bg_image = load_background_image()

# Function to load clues from a configuration file (JSON)
def load_clues(config_file='config.json'):
    if not os.path.exists(config_file):
        print(f"Config file '{config_file}' not found.")
        return []
    
    with open(config_file, 'r') as file:
        try:
            clues = json.load(file)
            return clues
        except json.JSONDecodeError:
            print(f"Error reading the config file '{config_file}'. Make sure it is valid JSON.")
            return []

# Load the clues from the config file
clues = load_clues()

# Variables
press_count = 0  # Keeps track of which clue to display
button_press_start_time = None
button_hold_duration = 3  # seconds for reset
reset_triggered = False

# Function to reset the app
def reset_app():
    global reset_triggered, press_count
    if not reset_triggered:
        print("Resetting the app...")
        press_count = 0
        reset_triggered = True

# Function to draw text on screen
def draw_text(text, size=48, color=(255, 255, 255)):
    font = pygame.font.SysFont("Helvetica", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text_surface, text_rect)

# Function to play a new clue
def play_new_clue(clue):
    pygame.mixer.stop()
    try:
        sound = pygame.mixer.Sound(clue["sound"])
        sound.play()
    except pygame.error as e:
        print(f"Error loading sound {clue['sound']}: {e}")

# Button press handler
def on_button_pressed():
    global button_press_start_time, reset_triggered, press_count
    button_press_start_time = time.time()
    print("Button Pressed!")
    
    if press_count >= len(clues):  # If all clues were played, show "No more clues"
        draw_text("No more clues.")
        pygame.display.update()
        press_count = 0  # Reset to the first clue on the next button press
    else:  # Play the next clue
        transition_to_clue(clues[press_count])
        press_count += 1

    reset_triggered = False

# Function to smoothly transition between clues
def transition_to_clue(clue):
    screen.fill((0, 0, 0))  # Fill the screen with black before displaying text
    pygame.display.update()
    draw_text(clue["text"])
    pygame.display.update()
    play_new_clue(clue)

# Check if the button is held
def check_button_hold():
    global button_press_start_time, reset_triggered
    if button.is_pressed:
        if button_press_start_time and (time.time() - button_press_start_time) >= button_hold_duration:
            reset_app()
    else:
        button_press_start_time = None

    pygame.time.wait(100)  # Delay to avoid overwhelming the CPU

# Function to safely exit when Escape key is pressed
def exit_program():
    print("Exiting Clue Box...")
    pygame.mixer.quit()
    pygame.quit()
    sys.exit(0)

# Main loop for the Pygame window
def main():
    global press_count
    if bg_image:
        screen.blit(bg_image, (0, 0))  # Draw the background image
    pygame.display.update()

    # Start the main event loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit_program()
        
        # Check if the button is pressed
        if button.is_pressed:
            on_button_pressed()

        # Check if the button is held
        check_button_hold()

    pygame.quit()

if __name__ == "__main__":
    main()
