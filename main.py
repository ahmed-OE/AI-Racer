import sys
import math
import pygame
from car import Car
from track_drawer import Track

pygame.init()

WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI-Racer")

clock = pygame.time.Clock()
FPS = 60

# Game Setup
track = Track(width=WIDTH, height=HEIGHT)
car = Car(track.start_x, track.start_y, (255, 0, 0))

# States: "DRAW" or "DRIVE"
state = "DRAW"

# Simple UI Font
font = pygame.font.SysFont("Arial", 16)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mode switching logic
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if state == "DRAW":
                    state = "DRIVE"
                    car = Car(track.start_x, track.start_y, (255, 0, 0))
                elif state == "DRIVE":
                    state = "DRAW"

        # Only pass drawing inputs to track when in DRAW mode
        if state == "DRAW":
            track.handle_event(event)

    # --- UPDATE LOGIC ---
    if state == "DRAW":
        track.update()

    elif state == "DRIVE":
        car.update() 

        # Collision Check
        if hasattr(track, "wall_rects") and len(track.wall_rects) > 0:
            hit_index = car.rect.collidelist(track.wall_rects)

            if hit_index != -1:
                print("Car on track")
            else:
                if car.direction == "forward":
                    car.speed = 0.2 
                elif car.direction == "reverse":
                    car.speed = -0.2
                    

    # --- DRAWING LOGIC ---
    screen.fill((0, 0, 0))
    
    # Always draw the track
    track.draw(screen)

    # Only render car when driving
    if state == "DRIVE":
        if hasattr(car, "draw"):
            car.draw(screen)
        else:
            screen.blit(car.image, car.rect)

    # Simple On-Screen Instruction Banner
    if state == "DRAW":
        banner_text = "MODE: Track Editor  |  Press SPACE to Drive"
        banner_color = (0, 255, 128)
    else:
        banner_text = "MODE: Driving  |  Press SPACE to Edit Track"
        banner_color = (255, 200, 0)

    text_surface = font.render(banner_text, True, banner_color)
    screen.blit(text_surface, (20, 20))

    clock.tick(FPS)
    pygame.display.flip()

pygame.quit()
sys.exit()