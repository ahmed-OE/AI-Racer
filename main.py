import sys
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
toggle_rays = 0   # 0 = off, 1 = on

# Simple UI Font
font = pygame.font.SysFont("Arial", 16)

running = True
while running:

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if state == "DRAW":
                    state = "DRIVE"
                    car = Car(track.start_x, track.start_y, (255, 0, 0))
                else:
                    state = "DRAW"

            if event.key == pygame.K_i:
                toggle_rays = 1 - toggle_rays   # flip between 0 and 1

        if state == "DRAW":
            track.handle_event(event)

    # ---------------- UPDATE ----------------
    if state == "DRAW":
        track.update()

    elif state == "DRIVE":
        car.update()

        # Calculate rays using the track surface (always, for AI)
        car.rays(track.surface)

        # Collision Check (color-based)
        center_x, center_y = int(car.position.x), int(car.position.y)
        if 0 <= center_x < track.width and 0 <= center_y < track.height:
            pixel_colour = track.surface.get_at((center_x, center_y))
            if pixel_colour.r < 50 and pixel_colour.g < 50 and pixel_colour.b < 50:
                if car.direction == "forward":
                    car.speed = 0.2
                elif car.direction == "reverse":
                    car.speed = -0.2

            if pixel_colour.r > 200 and pixel_colour.g > 200 and pixel_colour.b > 200 and car.speed > 0.5:
                car.finished = True
                print(car.finished)
            

    # ---------------- DRAW ----------------
    screen.fill((0, 0, 0))

    # Draw track
    track.draw(screen)

    if state == "DRIVE":
        # Draw car
        screen.blit(car.image, car.rect)

        # Draw rays only if toggled on
        if toggle_rays == 1:
            for start, end in car.rays_cords:
                pygame.draw.line(screen, (255, 255, 0), start, end, 2)
            for _, end in car.rays_cords:
                pygame.draw.circle(screen, (255, 0, 0), (int(end.x), int(end.y)), 4)

    # ---------------- UI ----------------
    if state == "DRAW":
        banner_text = "MODE: Track Editor | M: Drive | I: toggle rays"
        banner_color = (0, 255, 128)
    else:
        banner_text = "MODE: Driving | M: Edit Track | I: toggle rays"
        banner_color = (255, 200, 0)

    text_surface = font.render(banner_text, True, banner_color)
    screen.blit(text_surface, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()