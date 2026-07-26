import pygame
import math

RED = (255, 0, 0)

class Car(pygame.sprite.Sprite):

    def __init__(self, x, y, color,*groups):
        # Call the parent class (Sprite) constructor, passing along any groups
        super().__init__(*groups)

        # Pygame Sprites REQUIRE these two specific attribute names:
        self.image = pygame.Surface((30, 50))
        self.image.fill(color)

        self.rect = self.image.get_rect(center=(x, y))

        