import pygame
import sys

pygame.init()

screen_W = 1200
screen_H = 700
BLACK = (0, 0, 0)
GREY = (120, 120, 120)
WHITE = (255, 255, 255)
Track_brush_size = 30
Line_brush_size = 5
drawing = False

screen = pygame.display.set_mode((screen_W, screen_H))
pygame.display.set_caption("Track Drawer")

track = pygame.Surface((screen_W, screen_H))

tick_rate = pygame.time.Clock()

while True:

    screen.fill(GREY)
    screen.blit(track, (0, 0))

    for input in pygame.event.get():
        if input.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif input.type == pygame.MOUSEBUTTONDOWN:
            if input.button == 1:
                drawing = True

        elif input.type == pygame.MOUSEBUTTONUP:
            if input.button == 1:
                drawing = False          

        elif input.type == pygame.KEYDOWN:
            if input.key == pygame.K_c:
                track.fill(BLACK)

    if drawing:
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(track, GREY, mouse_pos, Track_brush_size)

    pygame.display.update()
    tick_rate.tick(120)

