import pygame

class Track:

    start_x = 100
    start_y = 100

    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((0, 0, 0))

        self.drawing = False
        self.wall_radius = 45
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
                self.start_line_set = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False

    def _place_segment(self, pos):
        radius = self.wall_radius - 5
        pygame.draw.circle(self.surface, (120, 120, 120), pos, radius)

    def update(self):
        if self.drawing:
            mouse_pos = pygame.mouse.get_pos()

            if self.last_draw_pos is None:
                self._place_segment(mouse_pos)
            else:
                last = pygame.math.Vector2(self.last_draw_pos)
                current = pygame.math.Vector2(mouse_pos)
                gap = current - last
                distance = gap.length()

                step_size = max(self.wall_radius - 5, 1) * 0.5

                if distance > step_size:
                    steps = int(distance // step_size)
                    for i in range(1, steps + 1):
                        point = last + gap * (i / steps)
                        self._place_segment((point.x, point.y))
                else:
                    self._place_segment(mouse_pos)

            self.last_draw_pos = mouse_pos

        # ---------- DRAW START LINE ON THE SURFACE ----------
        # This ensures it's visible for pixel‑color detection.
        if self.start_line_set and self.start_line_pos is not None:
            x, y = self.start_line_pos
            pygame.draw.line(
                self.surface,
                (255, 255, 255),
                (x + 30, y + 15),
                (x - 30, y + 15),
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
        return pixel.r > 200 and pixel.g > 200 and pixel.b > 200

    def draw(self, screen):
        # Blit the track surface (including the white line)
        screen.blit(self.surface, (0, 0))

    def clear(self):
        self.surface.fill((0, 0, 0))
        self.start_line_set = False
        self.start_line_pos = None
        self.last_draw_pos = None