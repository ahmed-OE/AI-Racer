import sys
import pygame
from car import Car
from track_drawer import Track
from Model import train_step   # import the training function

pygame.init()
WIDTH = 1200
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI-Racer")
clock = pygame.time.Clock()
FPS = 60

track = Track(width=WIDTH, height=HEIGHT)
car = Car(track.start_x, track.start_y, (255, 0, 0))

state = "DRAW"          # "DRAW" or "DRIVE"
training_mode = False   # True = AI trains, False = manual
toggle_rays = 0

font = pygame.font.SysFont("Arial", 16)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if state == "DRAW":
                    state = "DRIVE"
                    car = Car(track.start_x, track.start_y, (255, 0, 0))
                    training_mode = False
                else:
                    state = "DRAW"

            if event.key == pygame.K_i:
                toggle_rays = 1 - toggle_rays

            if state == "DRAW" and event.key == pygame.K_c:
                track.clear()

            if event.key == pygame.K_t and state == "DRIVE":
                training_mode = not training_mode
                if training_mode:
                    print("Training ON")
                    car = Car(track.start_x, track.start_y, (255, 0, 0))
                else:
                    print("Manual ON")

        if state == "DRAW":
            track.handle_event(event)

    # ---------- UPDATE ----------
    if state == "DRAW":
        track.update()

    elif state == "DRIVE":
        if training_mode:
            # AI training step (handles action, physics, reward, reset)
            train_step(car, track)
        else:
            # Manual driving
            car.handle_input()
            car.update()

        # Always update rays for visualisation and state (needed for both)
        car.rays(track.surface)

        # Collision / grass slow-down (kept for both modes)
        if track.is_off_track(car):
            if car.direction == "forward":
                car.speed = 0.2
            elif car.direction == "reverse":
                car.speed = -0.2

        # Finish line detection. Gated on car.left_start so the car doesn't
        # register a "finish" the instant it spawns on the line itself —
        # it has to actually drive away and come back around.
        if car.left_start and track.is_on_finish_line(car) and car.speed > 0.5:
            if not car.finished:
                print("Crossed line")
            car.finished = True
        else:
            car.finished = False

    # ---------- DRAW ----------
    screen.fill((0, 0, 0))
    track.draw(screen)

    if state == "DRIVE":
        screen.blit(car.image, car.rect)
        if toggle_rays == 1:
            for start, end in car.rays_cords:
                pygame.draw.line(screen, (255, 255, 0), start, end, 2)
            for _, end in car.rays_cords:
                pygame.draw.circle(screen, (255, 0, 0), (int(end.x), int(end.y)), 4)

    # UI
    if state == "DRAW":
        banner_text = "DRAW: Draw track | C: Clear | M: Drive"
        banner_color = (0, 255, 128)
    else:
        mode_text = "TRAINING" if training_mode else "MANUAL"
        banner_text = f"DRIVE: {mode_text} | T: toggle AI | M: Edit | I: toggle Rays"
        banner_color = (255, 200, 0)

    text_surface = font.render(banner_text, True, banner_color)
    screen.blit(text_surface, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()