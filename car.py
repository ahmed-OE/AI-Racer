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
        self.normal_traction = 0.18  # Snappy handling
        self.drift_traction = 0.02   # Smooth lateral slide

        self.is_drifting = False
        self.direction = "none"

        self.finished = False
        self.crashed = False

        # Used to gate finish-line detection: the car spawns ON the finish
        # line, so we only count a "finish" once it has actually driven
        # away from the start and come back around.
        self.start_pos = pygame.math.Vector2(x, y)
        self.left_start = False

        # Pygame Sprites REQUIRE these two specific attribute names:
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw body
        pygame.draw.rect(
            self.image,
            self.color,
            (0, 0, self.width, self.height),
            border_radius=6,
        )

        # Strip left
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

        # Engine shield
        pygame.draw.rect(
            self.image,
            (180, 220, 255),
            (6, self.height - 11, self.width - 12, 8),
            border_radius=2,
        )

        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(
            center=(int(self.position.x), int(self.position.y))
        )

    def rays(self, track_surface, max_distance=220):

        angle_offsets = [0, 20, -20, 40, -40, 70, -70]   # adjust as needed

        self.rays_dist = []
        self.rays_cords = []

        base_direction = pygame.math.Vector2(0, -1)
        width, height = track_surface.get_size()

        for offset in angle_offsets:

            direction = base_direction.rotate(-(self.angle + offset))
            distance = max_distance
            end_point = self.position + direction * max_distance

            # Step 3 pixels at a time for fast raycasting
            for step in range(1, max_distance + 1, 3):
                point = self.position + direction * step
                px, py = int(point.x), int(point.y)

                # Check if point is inside the track surface
                if 0 <= px < width and 0 <= py < height:
                    pixel_color = track_surface.get_at((px, py))
                    # If the pixel is dark (grass), we hit the track boundary
                    if pixel_color.r < 50 and pixel_color.g < 50 and pixel_color.b < 50:
                        distance = step
                        end_point = point
                        break
                else:
                    # Out of bounds → treat as grass
                    distance = step
                    end_point = point
                    break

            self.rays_dist.append(distance)
            self.rays_cords.append((self.position.copy(), end_point))

        return self.rays_dist, self.rays_cords

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Check drift mode state
        self.is_drifting = keys[pygame.K_SPACE] or keys[pygame.K_RSHIFT]

        current_max_speed = (
            self.drift_max_speed if self.is_drifting else self.max_speed
        )
        current_steering = (
            self.drift_steering if self.is_drifting else self.steering
        )

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
        traction = (self.drift_traction if self.is_drifting else self.normal_traction)

        # 4. Smoothly blend actual momentum toward target direction
        self.velocity = self.velocity.lerp(target_velocity, traction)

        # Apply displacement
        self.position += self.velocity

        # Keep angle in a sane range so angle_norm in Model.py stays in [-1, 1]
        self.angle %= 360
        if self.angle > 180:
            self.angle -= 360

        # Once the car has driven far enough from its spawn point, it's
        # allowed to trigger a finish-line crossing on the way back.
        if not self.left_start and self.position.distance_to(self.start_pos) > 100:
            self.left_start = True

        # Update sprite rotation & position
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(
            center=(int(self.position.x), int(self.position.y))
        )

    def reset(self, x, y):
        """Fully resets the car to a fresh episode/lap at (x, y)."""
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 0.0
        self.angle = 0.0
        self.direction = "none"
        self.is_drifting = False
        self.finished = False
        self.crashed = False
        self.start_pos = pygame.math.Vector2(x, y)
        self.left_start = False

        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(
            center=(int(self.position.x), int(self.position.y))
        )

    def apply_action(self, action):
    
        gas = False
        brake = False
        left = False
        right = False
        drift = False

        if action == 0:           # Coast
            pass
        elif action == 1:         # Gas
            gas = True
        elif action == 2:         # Brake
            brake = True
        elif action == 3:         # Left
            left = True
        elif action == 4:         # Right
            right = True
        elif action == 5:         # Gas + Left
            gas = True
            left = True
        elif action == 6:         # Gas + Right
            gas = True
            right = True
        elif action == 7:         # Brake + Left
            brake = True
            left = True
        elif action == 8:         # Brake + Right
            brake = True
            right = True
        elif action == 9:
            self.is_drifting = not self.is_drifting

        current_max_speed = self.drift_max_speed if self.is_drifting else self.max_speed
        current_steering = self.drift_steering if self.is_drifting else self.steering

        if gas:
            self.speed = min(self.speed + self.acceleration, current_max_speed)
            self.direction = "forward"
        elif brake:
            self.speed = max(self.speed - self.acceleration * 2, -self.R_max_speed)
            self.direction = "reverse"
        else:
            if self.speed > 0:
                self.speed = max(0.0, self.speed - self.friction)
            elif self.speed < 0:
                self.speed = min(0.0, self.speed + self.friction)

        if left and not right:
            self.angle += current_steering
        elif right and not left:
            self.angle -= current_steering