import pygame, math

pygame.init()
SCREEN_HEIGHT = 480
SCREEN_WIDTH = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
active_select = False
in_jump = False
running = True
t0 = None

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("BallMaster")

# Chargement de l'icône
icon = pygame.image.load("Sprites/golf-icon.png")
pygame.display.set_icon(icon)


class Ball:
    def __init__(self, pos, radius, color, mass, retention, velocity, id, friction):
        self.pos = pos
        self.radius = radius
        self.color = color
        self.mass = mass
        self.retention = retention
        self.velocity = velocity
        self.id = id
        self.friction = friction
        self.v0 = 0
        self.t0 = None  # Stocke le temps de début

    def draw(self):  # Dessine la balle
        self.circle = pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def weight(self):
        gravity = 0.5
        self.velocity += pygame.Vector2(0, gravity * self.mass)
        self.pos += self.velocity
        if self.pos.y >= SCREEN_HEIGHT - self.radius:
            self.pos.y = SCREEN_HEIGHT - self.radius
            self.velocity.y *= -self.retention
            if abs(self.velocity.y) <= 0.5:
                self.velocity.y = 0

    def ground_frictions(self):
        if self.pos.y >= SCREEN_HEIGHT - self.radius:
            if abs(self.velocity.y) < 0.05:
                friction_force = -self.friction * self.velocity.x
                self.velocity.x += friction_force
                if abs(self.velocity.x) < 0.01:
                    self.velocity.x = 0

    def moving(self):
        self.weight()
        self.ground_frictions()

    def shoot(self):
        angle = self.get_angle()
        force = pygame.math.Vector2(self.v0 * math.cos(math.radians(angle)), self.v0 * math.sin(math.radians(angle)))
        self.velocity += force / self.mass

    def check_select(self, pos):
        return abs(pos[0] - self.pos.x) < 10 and abs(pos[1] - self.pos.y) < 10

    def get_angle(self):
        pos = pygame.mouse.get_pos()
        dx = pos[0] - self.pos.x
        dy = self.pos.y - pos[1]
        if dx == 0:
            return 90
        elif dx < 0:
            return 180 - math.degrees(math.atan2(abs(dy), abs(dx)))
        return math.degrees(math.atan2(abs(dy), abs(dx)))

    def draw_trajectory(self, v0):
        if self.pos.y >= SCREEN_HEIGHT - self.radius:
            angle_deg = self.get_angle()
            angle_rad = math.radians(angle_deg)
            pos_x = [v0 * math.cos(angle_rad) * t + self.pos.x for t in range(0, 20, 2)]
            pos_y = [0.5 * 0.5 * t ** 2 - v0 * math.sin(angle_rad) * t + self.pos.y for t in range(0, 20, 2)]
            for i in range(len(pos_x)):
                pygame.draw.circle(screen, "red", (int(pos_x[i]), int(pos_y[i])), 4)

    def handle_shooting(self, event):
        """Gère la puissance de tir en fonction de l'appui sur ESPACE."""
        global active_select
        rate_v0 = 0.02  # Vitesse d'augmentation de la puissance
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.t0 = pygame.time.get_ticks()  # Début du chrono
            self.v0 = 0  # Réinitialisation de la puissance

        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and self.t0 is not None:
            duration = pygame.time.get_ticks() - self.t0  # Durée d'appui
            self.v0 = min(duration * rate_v0, 20)  # Limite de puissance
            self.shoot()  # Effectue le tir
            active_select = False
            self.t0 = None  # Réinitialise le chrono


ball = Ball(pygame.math.Vector2(250, 250), 7, (255, 255, 255), 0.5, 0.7, pygame.math.Vector2(0, 0), 1, 0.2)
while running:
    screen.fill((0, 0, 0))
    ball.moving()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and ball.check_select(event.pos):
                active_select = not active_select
        in_jump = True
        ball.handle_shooting(event)  # Gestion du tir dans la classe Ball

    if active_select:
        ball.draw_trajectory(10)
    ball.draw()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()

"""A faire : 
-collisions 
-Revoir toute la logique de la boucle principale, in_jump
draw tajectory à améliorer"""