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
    
    screen.fill((0, 0, 0))
    track.draw(screen)
    screen.blit(car.image, car.rect)

    if car.colliderect(track.surface.get_rect()):
        print("Car is on the track!")
    else:
        print("Car is off the track!")

    clock.tick(FPS)
    pygame.display.flip()

pygame.quit()
