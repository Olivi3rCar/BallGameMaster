import pygame,math

pygame.init()
SCREEN_HEIGHT = 480 ; SCREEN_WIDTH = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
active_select = False
in_jump = False
bounce = 0.5
space_pressed = False
running = True
t0 = None

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("BallMaster")

# Chargement de l'icône
icon = pygame.image.load("Sprites/golf-icon.png")
pygame.display.set_icon(icon)

class Ball:
    def __init__(self,pos,radius,color,mass,retention,velocity,id,friction):
        self.pos = pos
        self.radius = radius
        self.color = color
        self.mass = mass
        self.retention = retention
        self.velocity = velocity
        self.id = id
        self.friction = friction
        self.v0 = 0

    def draw(self): #Draws the ball
            self.circle = pygame.draw.circle(screen,self.color,(int(self.pos.x),int(self.pos.y)),self.radius)

    def weight(self):
        # Ajuste la gravité pour que la balle tombe plus naturellement (peut-être moins que 0.5 * self.mass)
        gravity = 0.5  # Ajuste cette valeur pour avoir un effet gravitationnel plus réaliste
        self.velocity += pygame.Vector2(0, gravity * self.mass)
        self.pos += self.velocity
        if self.pos.y >= SCREEN_HEIGHT - self.radius:
            self.pos.y = SCREEN_HEIGHT - self.radius
            self.velocity.y *= -self.retention
            if abs(self.velocity.y) <= bounce:
                self.velocity.y = 0  # Si la vitesse verticale est très faible, arrête-la complètement

    def ground_frictions(self):
        if self.pos.y >= SCREEN_HEIGHT - self.radius:  # La balle touche le sol
            if abs(self.velocity.y) < 0.05:  # Si elle ne rebondit plus (y presque nul)
                friction_force = -self.friction * self.velocity.x  # Applique une friction proportionnelle
                self.velocity.x += friction_force
                if abs(self.velocity.x) < 0.01:  # Seuil plus faible pour un arrêt progressif
                    self.velocity.x = 0

    def moving(self):
        self.weight()  # Applique le poids (gravité)
        self.ground_frictions()  # Applique la friction du sol

    def shoot(self,v0):
        angle = self.get_angle()
        force = pygame.math.Vector2(v0 * math.cos(math.radians(angle)), v0 * math.sin(math.radians(angle)))
        a = force/self.mass
        self.velocity += a

    def check_select(self,pos): #Function used to check whether we clicked on the ball or not
        return abs(pos[0] - self.pos.x)<10 and abs(pos[1] - self.pos.y)<10

    def get_angle(self): #Get the angle between the mouse and the ball (in degrees)
        pos = pygame.mouse.get_pos()
        dx = pos[0] - self.pos.x  # Distance horizontale
        dy = self.pos.y - pos[1]  # Distance verticale (sens positif vers le haut)
        # Si la souris est pile au-dessus ou en dessous de la balle
        if dx == 0:
            return 90
        elif dx < 0 :
            return 180 - math.degrees(math.atan2(abs(dy), abs(dx)))
        return math.degrees(math.atan2(abs(dy), abs(dx)))  # Toujours un angle entre 0 et 90°

    def draw_trajectory(self,v0):
        if self.pos.y >= SCREEN_HEIGHT - self.radius :
            angle_deg = self.get_angle()
            angle_rad = math.radians(angle_deg)  # Conversion en radians
            pos_x = [v0 * math.cos(angle_rad) * t + self.pos.x for t in range(0, 20,2)]
            pos_y = [0.5 * 0.5 * t ** 2 - v0 * math.sin(angle_rad) * t + self.pos.y for t in range(0, 20,2)]
            for i in range(len(pos_x)):
                pygame.draw.circle(screen, "red", (int(pos_x[i]), int(pos_y[i])), 4)

    def get_v0(self, t0, event):
        """Gère l'augmentation de v0 tant que la touche espace est enfoncée."""
        rate_v0 = 0.02  # Augmentation de la puissance par milliseconde
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            t0 = pygame.time.get_ticks()  # Démarrer le timer
            self.v0 =  0 # Réinitialiser v0 à 0
            return t0  # Retourne t0 pour qu'il soit mis à jour dans la boucle principale
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and t0 is not None: #Never get in this loop
            t1 = pygame.time.get_ticks()  # Temps quand on relâche
            duration = t1 - t0  # Durée d'appui en millisecondes
            self.v0 = min(duration * rate_v0, 10)  # Limite max de v0 à 20 pour éviter des valeurs extrêmes
            print(f"Puissance du tir : {self.v0}")  # Debug
            self.shoot(self.v0)  # Tirer avec la puissance calculée
            return None  # Réinitialiser t0 après le tir
        return t0  # Retourner t0 inchangé si aucun événement pertinent


    def search_collision(self,tiles):
        pass
        """look at self.x, and self.y then check until second to last row to search for the good height y, then search for the good x in the first row
        verify collision for all tiles in the intervall y(being a tile)+-1 and x(being a tile)+-1 """


ball = Ball(pygame.math.Vector2(250,250),7,(255,255,255),0.5,0.7,pygame.math.Vector2(0,0),1,0.2)
while running:
    screen.fill((0, 0, 0))
    ball.moving()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and ball.check_select(event.pos):
                active_select = not active_select

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not in_jump and active_select:
                in_jump = True
                t0 = pygame.time.get_ticks()  # Démarre le timer
                ball.v0 = 0  # Réinitialise v0

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and in_jump:
                duration = pygame.time.get_ticks() - t0  # Durée d'appui
                ball.v0 = min(duration * 0.02, 20)  # Limite v0
                print(f"Puissance du tir : {ball.v0}")  # Debug
                ball.shoot(ball.v0)  # Tirer avec la puissance calculée
                in_jump = False  # Réinitialise in_jump

    if active_select:
        ball.draw_trajectory(10)

    ball.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

"""A faire : 
-collisions 
-Revoir toute la logique de la boucle principale
draw tajectory à améliorer"""