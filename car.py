import math
import pygame

RED = (255, 0, 0)


class Car(pygame.sprite.Sprite):

    def __init__(self, x, y, color=RED, *groups):
        # Call the parent class (Sprite) constructor, passing along any groups
        super().__init__(*groups)

        self.x = float(x)
        self.y = float(y)

        self.width = 29
        self.height = 48
        self.color = color

        # Pygame Sprites REQUIRE these two specific attribute names:
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw body
        pygame.draw.rect(
            self.image,
            self.color,
            (0, 0, self.width, self.height),
            border_radius=6,
        )

        # strip left
        pygame.draw.rect(
            self.image,
            (180, 180, 180),
            (11, 0, 3, self.height - 1),
            border_radius=6,
        ) 

        pygame.draw.rect(
            self.image,
            (180, 180, 180),
            (15, 0, 3, self.height - 1),
            border_radius=6,
        ) 

        # Windshield
        pygame.draw.rect(
            self.image,
            (180, 220, 255),
            (4, 14, self.width - 8, 10),
            border_radius=2,
        )

        # engine_shield
        pygame.draw.rect(
                    self.image,
                    (180, 220, 255),
                    (6, self.height - 11, self.width - 12, 8),
                    border_radius=2,
                )


        # REMOVED: self.image.fill(color) <-- This line was erasing your windshield!

        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))