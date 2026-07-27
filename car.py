import math
import pygame

RED = (255, 0, 0)


class Car(pygame.sprite.Sprite):

    def __init__(self, x, y, color=RED, *groups):
        super().__init__(*groups)

        # 1. Use Vector2 for 2D position and momentum
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)

        self.width = 29
        self.height = 48
        self.color = color

        self.speed = 0.0
        self.angle = 0.0 
        
        # Standard driving parameters
        self.steering = 2.5
        self.acceleration = 0.05
        self.max_speed = 5.0
        self.R_max_speed = 2.5
        self.friction = 0.05

        # Drift parameters
        self.drift_steering = 3.2
        self.drift_max_speed = 4.0
        
        # 2. Traction controls lateral grip (0.0 = ice, 1.0 = glued to rails)
        self.normal_traction = 0.18   # Snappy handling
        self.drift_traction = 0.02    # Smooth lateral slide

        self.is_drifting = False
        self.direction = "none"

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
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Check drift mode state
        self.is_drifting = keys[pygame.K_SPACE] or keys[pygame.K_RSHIFT]

        current_max_speed = self.drift_max_speed if self.is_drifting else self.max_speed
        current_steering = self.drift_steering if self.is_drifting else self.steering

        # ACCELERATION & REVERSE
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, current_max_speed)
            self.direction = "forward"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.R_max_speed)
            self.direction = "reverse"
        else:              
            if self.speed > 0:
                self.speed = max(0.0, self.speed - self.friction)
            elif self.speed < 0:
                self.speed = min(0.0, self.speed + self.friction)
        
        # STEERING
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= current_steering
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += current_steering

    def update(self):
        self.handle_input()

        # 3. Heading direction vector (where the nose points)
        forward_dir = pygame.math.Vector2(0, -1).rotate(-self.angle)
        
        # Target velocity based purely on engine throttle & body orientation
        target_velocity = forward_dir * self.speed

        # Select traction grip based on drift state
        traction = self.drift_traction if self.is_drifting else self.normal_traction

        # 4. Smoothly blend actual momentum toward target direction
        self.velocity = self.velocity.lerp(target_velocity, traction)

        # Apply displacement
        self.position += self.velocity

        # Update sprite rotation & position
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))