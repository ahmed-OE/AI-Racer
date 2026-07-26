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

        self.speed = 0.0
        self.angle = 0.0 
        self.steering = 2.5
        self.acceleration = 0.2
        self.max_speed = 5.0
        self.R_max_speed = 2.5
        self.friction = 0.05

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

        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def handle_input(self):
        keys = pygame.key.get_pressed()

    # 1. ACCELERATION & REVERSE
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.R_max_speed)
        else:
           
            if self.speed > 0:
                self.speed = max(0.0, self.speed - self.friction)
            elif self.speed < 0:
                self.speed = min(0.0, self.speed + self.friction)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= self.steering
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += self.steering

    def update(self):
        self.handle_input()

        # Trigonometry movement math
        radians = math.radians(self.angle)
        self.x += self.speed * math.sin(-radians)
        self.y -= self.speed * math.cos(-radians)

        # Rotate from base master image to prevent graphic distortion
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))