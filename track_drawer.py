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

        # LIST TO STORE INDIVIDUAL WALL RECTANGLES FOR COLLIDERECT
        self.wall_rects = []

        self.drawing = False
        self.wall_radius = 35  # Size of outer border wall

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drawing = True
            mouse_pos = pygame.mouse.get_pos()
            self.start_x = mouse_pos[0]
            self.start_y = mouse_pos[1]
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False

    def update(self):
        """Draws track visuals AND creates collision rectangles for walls."""
        if self.drawing:
            mouse_pos = pygame.mouse.get_pos()

            # 1. Create a small Rect for the wall segment at current mouse position
            wall_rect = pygame.Rect(
                mouse_pos[0] - self.wall_radius,
                mouse_pos[1] - self.wall_radius,
                self.wall_radius * 0.9,
                self.wall_radius * 0.9,
            )
       
            self.wall_rects.append(wall_rect)

            pygame.draw.circle(self.surface, (120, 120, 120), mouse_pos, self.wall_radius - 5)

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))