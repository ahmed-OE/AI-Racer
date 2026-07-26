import pygame


class Track:

    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height

        # Colors
        self.BLACK = (0, 0, 0)
        self.GREY = (120, 120, 120)
        self.RED = (255, 0, 0)

        # Brush settings
        self.track_brush_size = 30
        self.line_brush_size = 5

        # Drawing state
        self.drawing = False

        # Create track surface canvas
        self.surface = pygame.Surface((self.width, self.height))
        self.clear()

    def handle_event(self, event):
        """Processes mouse input for drawing and keyboard input for clearing."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.drawing = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.drawing = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.clear()

    def update(self):
        """Draws road segments onto the track surface while holding left click."""
        if self.drawing:
            mouse_pos = pygame.mouse.get_pos()

            pygame.draw.circle(self.surface, self.GREY, mouse_pos, self.track_brush_size)

    def clear(self):
        """Resets the track surface back to solid black."""
        self.surface.fill(self.BLACK)

    def draw(self, screen):
        """Renders the track canvas onto the main display window."""
        screen.blit(self.surface, (0, 0))