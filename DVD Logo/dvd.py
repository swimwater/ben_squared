import os
import pygame
import sys
import random
import cairosvg
import imageio

from io import BytesIO
from xml.dom.minidom import parseString
from datetime import datetime
from PIL import Image
from pathlib import Path

script_dir = Path(__file__).parent
sound_path = script_dir / "sounds"
image_path = script_dir / "images"
gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"


if os.path.exists(gtk_path):
    os.add_dll_directory(gtk_path)
else:
    print(f"GTK3 runtime not found at {gtk_path}. Ensure it's installed correctly.")


class DVDLogo():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Bouncing DVD Screensaver")

        # (16:9 aspect ratio - Full HD)
        self.screen_width = 1280
        self.screen_height = 720
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        self.background_color = (0, 0, 0)
        self.font_color = (255, 255, 255)
        self.font = pygame.font.SysFont(name=None, size=36, bold=False, italic=False)

        self.logo_width = 200
        self.logo_height = 100

        self.svg_path = Path(image_path, 'DVD-Video_logo.svg')
        self.__load_svg_with_color()
        self.dvd_logo_rect = self.dvd_logo.get_rect()
        self.dvd_logo_rect.x = random.randint(0, self.screen_width - self.dvd_logo_rect.width)
        self.dvd_logo_rect.y = random.randint(0, self.screen_height - self.dvd_logo_rect.height)

        self.speed_x = 1
        self.speed_y = 1

        self.corner_count = 0
        self.corner_hit_sounds = ["yipee.mp3", "Ode_To_Joy.mp3", "Yay.mp3", "Happy_Wheels.mp3", "Bonk.mp3"]
        self.corner_hit_volume = 0.25  # Volume for corner hit sounds (0.0 to 1.0)

        self.gif_frames = self.__get_gif_frames()
        self.gif_duration = 5 # In seconds
        if self.gif_frames:
            self.gif_frame_duration = self.gif_duration / len(self.gif_frames)  # Total gif duration divided by the number of frames
        else:
            self.gif_frame_duration = 0

    def launch_screen_saver(self):
        gif_start_time = None

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Move the logo
            self.dvd_logo_rect.x += self.speed_x
            self.dvd_logo_rect.y += self.speed_y

            # Bounce off the edges and change color
            if self.dvd_logo_rect.left <= 0 or self.dvd_logo_rect.right >= self.screen_width:
                self.speed_x = -self.speed_x
                self.__load_svg_with_color()
            if self.dvd_logo_rect.top <= 0 or self.dvd_logo_rect.bottom >= self.screen_height:
                self.speed_y = -self.speed_y
                self.__load_svg_with_color()

            if self.__corner_hit():
                gif_start_time = datetime.now()

            # Set screen background (clear previous elements)
            self.screen.fill(self.background_color)

            # Check if we should be displaying the GIF
            if gif_start_time and (datetime.now() - gif_start_time).total_seconds() < self.gif_duration:
                elapsed_time = (datetime.now() - gif_start_time).total_seconds()
                gif_frame_index = int((elapsed_time / self.gif_frame_duration) % len(self.gif_frames))
                self.screen.blit(self.gif_frames[gif_frame_index], (0, 0))

            # Draw the DVD logo on the screen
            self.screen.blit(self.dvd_logo, self.dvd_logo_rect)

            # Render the corner counter if it is greater than 0
            if self.corner_count > 0:
                counter_text = self.font.render(f"Corner Hits: {self.corner_count}", True, self.font_color)
                self.screen.blit(counter_text, (10, 10))

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            self.clock.tick(120)

    # Function to generate a random color
    def __random_color(self):
        return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Function to convert SVG to a Pygame surface with a specified color and resize
    def __load_svg_with_color(self):
        # Read the SVG file
        try:
            with open(self.svg_path, 'r') as file:
                svg_data = file.read()
        except FileNotFoundError:
            print(f"SVG file not found at {self.svg_path}. Ensure the file exists.")
            pygame.quit()
            sys.exit()

        # Parse the SVG and change its color
        dom = parseString(svg_data)
        for path in dom.getElementsByTagName('path'):
            path.setAttribute('fill', self.__random_color())

        # Convert the colored SVG data to PNG with resizing
        png_data = cairosvg.svg2png(bytestring=dom.toxml(), output_width=self.logo_width, output_height=self.logo_height)

        # Load the PNG data into a Pygame surface
        try:
            self.dvd_logo = pygame.image.load(BytesIO(png_data))
        except pygame.error as e:
            print(f"Error loading PNG data into Pygame surface: {e}")
            pygame.quit()
            sys.exit()
    
    def __get_gif_frames(self) -> list:
        gif_path = Path(image_path, "confetti.gif")
        if not gif_path.exists():
            print(f"GIF file not found at {gif_path}. Ensure the file exists.")
            return []

        try:
            gif = imageio.mimread(gif_path)
        except Exception as e:
            print(f"Error reading GIF file: {e}")
            return []
        
        gif_frames = []
        for frame in gif:
            pil_image = Image.fromarray(frame).resize((self.screen_width, self.screen_height), Image.LANCZOS)
            pygame_image = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)
            gif_frames.append(pygame_image)
        return gif_frames

    def __corner_hit(self) -> bool:
        # Check for corner hit
        corner_hit = (
            (self.dvd_logo_rect.left <= 0 or self.dvd_logo_rect.right >= self.screen_width) and
            (self.dvd_logo_rect.top <= 0 or self.dvd_logo_rect.bottom >= self.screen_height)
        )

        # Increment corner counter and play random sound if a corner was hit
        if corner_hit:
            self.corner_count += 1
            sound_file = Path(sound_path, random.choice(self.corner_hit_sounds))
            if sound_file.exists():
                try:
                    corner_hit_sound = pygame.mixer.Sound(sound_file)
                    corner_hit_sound.set_volume(self.corner_hit_volume)
                    corner_hit_sound.play()
                except pygame.error as e:
                    print(f"Error playing sound {sound_file}: {e}")
            else:
                print(f"Sound file {sound_file} does not exist.")
            return True
        return False

if __name__ == "__main__":
    dvd_logo = DVDLogo()
    dvd_logo.launch_screen_saver()