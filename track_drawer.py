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

    def draw(self, screen):
        # Blit the track surface (including the white line)
        screen.blit(self.surface, (0, 0))