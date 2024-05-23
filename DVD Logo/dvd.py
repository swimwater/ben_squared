import os
os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")

import pygame
import sys
import random
import cairosvg
from io import BytesIO
from xml.dom.minidom import parseString
import imageio
from datetime import datetime
from PIL import Image
from pathlib import Path

sound_path = Path("sounds")
image_path = Path("images")

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions (16:9 aspect ratio - Full HD)
screen_width = 1280
screen_height = 720

# Colors
background_color = (0, 0, 0)
font_color = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bouncing DVD Screensaver")

# Font for corner counter
font = pygame.font.SysFont(None, 36)

# Function to generate a random color
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Function to convert SVG to a Pygame surface with a specified color and resize
def load_svg_with_color(svg_path, color, width, height):
    # Read the SVG file
    with open(svg_path, 'r') as file:
        svg_data = file.read()

    # Parse the SVG and change its color
    dom = parseString(svg_data)
    for path in dom.getElementsByTagName('path'):
        path.setAttribute('fill', color)

    colored_svg_data = dom.toxml()

    # Convert the colored SVG data to PNG with resizing
    png_data = cairosvg.svg2png(bytestring=colored_svg_data, output_width=width, output_height=height)

    # Load the PNG data into a Pygame surface
    image = pygame.image.load(BytesIO(png_data))
    return image

# Desired logo size
logo_width = 200
logo_height = 100

# Load the initial DVD logo
svg_path = Path(image_path, 'DVD-Video_logo.svg')
dvd_color = random_color()
dvd_logo = load_svg_with_color(svg_path, dvd_color, logo_width, logo_height)
dvd_logo_rect = dvd_logo.get_rect()

# Initial position and speed
dvd_logo_rect.x = random.randint(0, screen_width - dvd_logo_rect.width)
dvd_logo_rect.y = random.randint(0, screen_height - dvd_logo_rect.height)
speed_x = 20
speed_y = 20

# Corner hit counter
corner_count = 0

# List of corner hit sound files
corner_hit_sounds = ["yipee.mp3", "Ode_To_Joy.mp3", "Yay.mp3", "Happy_Wheels.mp3", "Bonk.mp3"]
corner_hit_volume = 0.25  # Volume for corner hit sounds (0.0 to 1.0)

# Load the GIF
gif_path = Path(image_path, "confetti.gif")  # Path to your GIF
gif = imageio.mimread(gif_path)

# Convert GIF frames to Pygame surfaces using PIL and resize them
gif_frames = []
for frame in gif:
    pil_image = Image.fromarray(frame).resize((screen_width, screen_height), Image.LANCZOS)
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    pygame_image = pygame.image.fromstring(data, size, mode)
    gif_frames.append(pygame_image)

gif_frame_duration = 5 / len(gif_frames)  # 5 seconds divided by the number of frames

# Main loop
clock = pygame.time.Clock()
gif_start_time = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Move the logo
    dvd_logo_rect.x += speed_x
    dvd_logo_rect.y += speed_y

    # Check for corner hit
    corner_hit = (dvd_logo_rect.left <= 0 and dvd_logo_rect.top <= 0) or \
                 (dvd_logo_rect.right >= screen_width and dvd_logo_rect.top <= 0) or \
                 (dvd_logo_rect.left <= 0 and dvd_logo_rect.bottom >= screen_height) or \
                 (dvd_logo_rect.right >= screen_width and dvd_logo_rect.bottom >= screen_height)

    # Bounce off the edges and change color
    if dvd_logo_rect.left <= 0 or dvd_logo_rect.right >= screen_width:
        speed_x = -speed_x
        dvd_color = random_color()
        dvd_logo = load_svg_with_color(svg_path, dvd_color, logo_width, logo_height)
    if dvd_logo_rect.top <= 0 or dvd_logo_rect.bottom >= screen_height:
        speed_y = -speed_y
        dvd_color = random_color()
        dvd_logo = load_svg_with_color(svg_path, dvd_color, logo_width, logo_height)

    # Increment corner counter and play random sound if a corner was hit
    if corner_hit:
        corner_count += 1
        corner_hit_sound = pygame.mixer.Sound(Path(sound_path, random.choice(corner_hit_sounds)))
        corner_hit_sound.set_volume(corner_hit_volume)
        corner_hit_sound.play()
        gif_start_time = datetime.now()

    # Fill the screen with the background color
    screen.fill(background_color)

    # Check if we should be displaying the GIF
    if gif_start_time and (datetime.now() - gif_start_time).total_seconds() < 5:
        elapsed_time = (datetime.now() - gif_start_time).total_seconds()
        gif_frame_index = int((elapsed_time / gif_frame_duration) % len(gif_frames))
        screen.blit(gif_frames[gif_frame_index], (0, 0))

    # Draw the DVD logo on the screen
    screen.blit(dvd_logo, dvd_logo_rect)

    # Render the corner counter if it is greater than 0
    if corner_count > 0:
        counter_text = font.render(f"Corner Hits: {corner_count}", True, font_color)
        screen.blit(counter_text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
