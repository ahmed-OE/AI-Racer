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

track = Track(width=WIDTH, height=HEIGHT)
car = Car(WIDTH // 2, HEIGHT // 2, (255, 0, 0))

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        track.handle_event(event)

    track.update()
    car.update() 

    if hasattr(track, "wall_rects") and len(track.wall_rects) > 0:
        hit_index = car.rect.collidelist(track.wall_rects)

        if hit_index != -1:
            print("Car is touching the track")
            
        else:
            print("Car is outside the track!")


    screen.fill((0, 0, 0))
    track.draw(screen)

    if hasattr(car, "draw"):
        car.draw(screen)
    else:
        screen.blit(car.image, car.rect)

    clock.tick(FPS)
    pygame.display.flip()

pygame.quit()