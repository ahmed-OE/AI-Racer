import pygame

class Track:

    start_x = 100
    start_y = 100
    spawn_car_x = -50
    spawn_car_y = -50
    draw_count = 0
    last_time = 0



    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height
        self.checkpoints = []
        self.marker_pos = None

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((0, 0, 0))

        self.drawing = False
        self.last_draw_pos = None

        # Start line data
        self.start_line_pos = None
        self.start_line_set = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drawing = True
            mouse_pos = pygame.mouse.get_pos()
            self.start_x = mouse_pos[0]
            self.start_y = mouse_pos[1]
            self.last_draw_pos = None

            # Store the start line position on the very first click
            if not self.start_line_set:
                self.start_line_pos = mouse_pos
                self.spawn_car_x = mouse_pos[0]
                self.spawn_car_y = mouse_pos[1]
                self.start_line_set = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False

    def _place_segment(self, pos, Track_size, mode): #drawing mode

        if mode == "Track":
            radius = Track_size - 5
            pygame.draw.circle(self.surface, (120, 120, 120), pos, radius)
        elif mode == "Drift-D":
            pygame.draw.circle(self.surface, (255, 220, 50), pos, (Track_size * 0.30))
        elif mode == "Drift-C":
            pygame.draw.circle(self.surface, (120, 120, 120), pos, (Track_size * 0.50))

    def update(self, Track_size, mode):
        if self.drawing:
            mouse_pos = pygame.mouse.get_pos()

            if self.last_draw_pos is None:
                self._place_segment(mouse_pos, Track_size, mode)
            else:
                last = pygame.math.Vector2(self.last_draw_pos)
                current = pygame.math.Vector2(mouse_pos)
                gap = current - last
                distance = gap.length()

                step_size = max(Track_size - 5, 1) * 0.5


                if mode == "Track":
                    current_time = pygame.time.get_ticks()

                    if current_time - self.last_time >= 1000:
                        self.checkpoints.append((len(self.checkpoints) + 1, current.copy()))
                        self.last_time = current_time
                        self.marker_pos = current.copy()
                        print(self.checkpoints)
                

                if distance > step_size:
                    steps = int(distance // step_size)
                    for i in range(1, steps + 1):
                        point = last + gap * (i / steps)
                        self._place_segment((point.x, point.y), Track_size, mode)
                        
                else:
                    self._place_segment(mouse_pos, Track_size, mode)

            self.last_draw_pos = mouse_pos

        # ---------- DRAW START LINE ON THE SURFACE ----------
        # This ensures it's visible for pixel‑color detection.
        if self.start_line_set and self.start_line_pos is not None:
            x, y = self.start_line_pos
            pygame.draw.line(
                self.surface,
                (255, 255, 255),
                (x + (Track_size * 0.65), y + (Track_size * 0.33)),
                (x - (Track_size * 0.65), y + (Track_size * 0.33)),
                8
            )

    def get_pixel(self, x, y):
        """Returns the surface pixel color at (x, y), or None if out of bounds."""
        px, py = int(x), int(y)
        if 0 <= px < self.width and 0 <= py < self.height:
            return self.surface.get_at((px, py))
        return None

    def is_off_track(self, car):
        """True if the car's center is on grass (dark pixel) or off the surface."""
        pixel = self.get_pixel(car.position.x, car.position.y)
        if pixel is None:
            return True
        return pixel.r < 50 and pixel.g < 50 and pixel.b < 50

    def is_on_finish_line(self, car):
        """True if the car's center is on the white start/finish line."""
        pixel = self.get_pixel(car.position.x, car.position.y)
        if pixel is None:
            return False
        return pixel.r > 250 and pixel.g > 250 and pixel.b > 250

    def is_on_reward(self, car):
        pixel = self.get_pixel(car.position.x, car.position.y)

        if pixel is None:
            return False

        reward_cord = pygame.math.Vector2(car.position.x, car.position.y)
        if pixel.r > 80 and pixel.g > 80 and pixel.b > 80:
            return reward_cord
        return False

    def draw(self, screen):
        # Blit the track surface (including the white line)
        screen.blit(self.surface, (0, 0))

    def clear(self):
        self.surface.fill((0, 0, 0))
        self.start_line_set = False
        self.start_line_pos = None
        self.last_draw_pos = None