import pygame

class Track:

    start_x = 100
    start_y = 100

    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height

        # Canvas surface for visual road rendering
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((0, 0, 0))  # Grass background

        self.drawing = False
        self.wall_radius = 45  # Size of outer border wall

        self.last_draw_pos = None  # last point a segment was placed at, for gap-filling

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drawing = True
            mouse_pos = pygame.mouse.get_pos()
            self.start_x = mouse_pos[0]
            self.start_y = mouse_pos[1]
            self.last_draw_pos = None  # reset so the first point of a new stroke always places
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False

    def _place_segment(self, pos):
        """Draws one track segment as a visual circle."""
        radius = self.wall_radius - 5
        pygame.draw.circle(self.surface, (120, 120, 120), pos, radius)

    def update(self):
        """Draws track visuals as the user drags the mouse."""
        if self.drawing:
            mouse_pos = pygame.mouse.get_pos()

            if self.last_draw_pos is None:
                # First point of this stroke
                self._place_segment(mouse_pos)
            else:
                # Fill the gap between the last placed point and the current mouse
                # position so a fast drag doesn't leave holes in the track.
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

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))