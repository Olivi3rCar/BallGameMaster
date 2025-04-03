import pygame
import math
from SAT_algorithm_collision import *  # Si tu utilises un module externe, sinon ignorez cette ligne
from tiles import *
# ---------------------------
# Initialization of Pygame window parameters
# ---------------------------
pygame.init()
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("BallMaster")
icon = pygame.image.load("Sprites/golf-icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
running = True
active_select = False
in_jump = False
running = True
t0 = None

def draw_hitbox(ball, tile):
    if collision_check(tile.vertices, (ball.pos.x, ball.pos.y), ball.radius):
        pygame.draw.polygon(screen, "green", tile.vertices)


# ---------------------------
# Class Ball
# ---------------------------

"""la balle reste coincee sur une pente sans retomber + le vecteur normal de la tile ou se situe la balle affecte la direction du saut + pas toujours les tiles les plus pertinantes
le vecteur est toujours le bon, sauf si la balle est trop rapide

solution pour le choix des tiles, gonfler artificiellement la hitbox des tiles pentes
tile 8 la balle touche deux edges en meme temps, donc l'algo renvoie le mauvais vecteur normal"""

class Ball:
    def __init__(self, pos, radius, mass, retention, velocity, id, friction):
        self.pos = pos
        self.radius = radius
        self.mass = mass
        self.retention = retention
        self.velocity = velocity
        self.id = id
        self.friction = friction
        self.v0 = None
        self.shot_state = [False, 0]
        self.normal_vector = pygame.math.Vector2(0,0)

    def freeze_normal_vect(self):
        if self.shot_state[0] :
            self.shot_state[0] -= 1
            if self.shot_state[1] <= 0 :
                self.shot_state[0] = False


    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.radius)

    def bounce(self):
        normal_velocity_component = self.velocity.dot(self.normal_vector) * self.normal_vector
        reflected_velocity = normal_velocity_component * -(1 + self.retention)

        # Condition pour arrêter les petits rebonds
        if reflected_velocity.length() < 0.5:  # Seuil pour stopper les rebonds
            return pygame.Vector2(0, 0)
        return reflected_velocity

    def is_normal_good(self,tile): #Make sure we have the good normal_vector
        # Normalize the normal vector
        self.normal_vector = pygame.Vector2(self.normal_vector).normalize()
        # Test position
        pos_test = self.pos + 10*self.normal_vector
        # Check for collision
        if collision_check(tile.vertices, (pos_test.x, pos_test.y), self.radius):
            self.normal_vector = -self.normal_vector
        return False

    def is_tangent_good(self,tangent_vector):
        if abs(self.velocity.x + tangent_vector.x) != abs(self.velocity.x) + abs(tangent_vector.x) or abs(self.velocity.y + tangent_vector.y) != abs(self.velocity.y) + abs(tangent_vector.y) :
            return -tangent_vector
        return tangent_vector

    def weight(self):
        gravity = pygame.Vector2(0, 0.4)  # gravity
        return gravity * self.mass

    def frictions(self,tangent_vector): #tengent not good
        if self.is_on_valid_surface():
            # Force de friction (proportionnelle à la vitesse actuelle)
            friction_force = -self.velocity.dot(tangent_vector) * self.friction * tangent_vector

            # Vérification si la force de friction est trop grande par rapport à la vitesse actuelle
            if friction_force.length() > self.velocity.length():
                # On applique une petite friction, mais pas plus que la vitesse
                friction_force = -self.velocity

            # Appliquer la friction en diminuant progressivement la vitesse
            # Si la vitesse est faible, on réduit la friction de manière progressive
            if self.velocity.length() < 0.5:  # Si la vitesse est très faible
                friction_force = -self.velocity  # Appliquer une friction plus douce pour finir l'arrêt en douceur

            return friction_force

        return pygame.Vector2(0, 0)

    def is_on_valid_surface(self):
        slope_angle = self.getting_slope_angle()
        return abs(slope_angle-90) > 20  # (No frictions against a wall)

    def moving(self, tilemap):
        weight = self.weight()
        if self.shot_state[0] :
            self.normal_vector = pygame.math.Vector2(0,0)
            while self.shot_state[1] > 0 :
                self.shot_state[1] -= 1
            self.shot_state[0] = False
        else :
            collision_info = self.handle_collision(tilemap) #THE Dictionnary CONTAINING INFOS ABOUT THE TILES THAT ARE TOUCHING
            if collision_info:
                for tile_key in collision_info.keys():
                    draw_hitbox(self,tile_key)
                    self.normal_vector = collision_info[tile_key][0]
                    self.is_normal_good(tile_key)
                    tangent_vector = pygame.Vector2(-self.normal_vector.y, self.normal_vector.x)  # tangent vector to the normal
                    penetration = collision_info[tile_key][1]
                    tangent_vector = self.is_tangent_good(tangent_vector)
                    self.repositioning(penetration)
                    # forces decomposition
                    normal_force = weight.dot(self.normal_vector) * self.normal_vector
                    parallel_force = weight.dot(tangent_vector) * tangent_vector
                    self.velocity += -parallel_force + normal_force
                    self.velocity += self.frictions(tangent_vector) #PROBLEME AVEC LES FROTTEMENTS
                    self.velocity += self.bounce()
                    if abs(self.velocity.y) < 0.21:  # Si la vitesse verticale est trop faible
                        self.velocity.y = 0  # On annule la vitesse verticale, mais on conserve la vitesse horizontale
                        # Appliquer une petite composante de mouvement même sur une pente très douce
                        if abs(self.velocity.x) < 0.01:  # Si la vitesse horizontale est très faible
                           self.velocity.x = 0  # Arrêt total, on peut aussi ajuster ce seuil pour plus de fluidité
            else:
                self.velocity += weight

        self.pos += self.velocity


    def repositioning(self, penetration):
        #to reposition the ball, the epsilon is to make sure the ball isn't stuck
        epsilon = 0.1
        self.pos += self.normal_vector * (penetration + epsilon)


    def getting_slope_angle(self):
        if self.normal_vector.x == 0:
            return 90 if self.normal_vector.y > 0 else -90
        return math.degrees(math.atan2(self.normal_vector.y, self.normal_vector.x))

    def handle_collision(self, tilemap):
        collision_tiles = {}
        ANGLE_THRESHOLD = 10  # Seuil pour considérer deux normales comme similaires
        EDGE_ANGLE_THRESHOLD = 75  # Seuil pour détecter un contact avec une arête

        for tile in tilemap.tiles:
            collision = collision_check(tile.vertices, (self.pos.x, self.pos.y), self.radius)

            if collision:
                normal_vector = pygame.Vector2(collision[0]).normalize()
                overlap = collision[1]

                # Vérifier si on touche déjà une autre normale avec un angle proche de 90° (arête)
                added = False
                for existing_tile, (existing_normal, existing_overlap) in list(collision_tiles.items()):
                    angle_between = abs(existing_normal.angle_to(normal_vector))

                    if angle_between < ANGLE_THRESHOLD:
                        # Même direction, on garde celui avec le plus grand overlap
                        if overlap > existing_overlap:
                            collision_tiles[existing_tile] = (normal_vector, overlap)
                        added = True
                        break

                    elif angle_between > EDGE_ANGLE_THRESHOLD:
                        # Collision avec une arête détectée -> Prendre la plus pertinente
                        if overlap > existing_overlap:
                            collision_tiles.clear()  # Priorité à la plus forte pénétration
                            collision_tiles[tile] = (normal_vector, overlap)
                        added = True
                        break

                if not added:
                    if len(collision_tiles) < 2:
                        collision_tiles[tile] = (normal_vector, overlap)

        return collision_tiles if collision_tiles else False

    def shoot(self):
        angle = self.get_trajectory_angle()
        self.shot_state = [True, 10]
        force = pygame.math.Vector2(self.v0 * (math.cos(math.radians(angle))), self.v0 * (math.sin(math.radians(angle))))
        # Reset any existing velocity completely
        self.velocity = force / self.mass
        print(f"angle : {angle}, normal_vector : {self.normal_vector}  velocity : {self.velocity}")


    def get_trajectory_angle(self):
        pos = pygame.mouse.get_pos()
        dx = pos[0] - self.pos.x
        dy = self.pos.y - pos[1]
        if dx == 0:
            return 90
        elif dx < 0:
            return 180 - math.degrees(math.atan2(abs(dy), abs(dx)))
        return math.degrees(math.atan2(abs(dy), abs(dx)))

    def check_select(self, pos):
        return abs(pos[0] - self.pos.x) < 10 and abs(pos[1] - self.pos.y) < 10

    def draw_trajectory(self, v0):
        angle_deg = self.get_trajectory_angle()
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

        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and self.t0 is not None and active_select:
            duration = pygame.time.get_ticks() - self.t0  # Durée d'appui
            self.v0 = min(duration * rate_v0, 10)  # Limite de puissance
            self.shoot()  # Effectue le tir
            active_select = False
            self.t0 = None  # Réinitialise le chrono


# ---------------------------
# Charging the items
# ---------------------------
spritesheet = Spritesheet(os.path.join("Sprites png/sandtiles.png"), tile_size=32, columns=9)
tilemap = Tilemap("tiles_maps/test_map.csv", spritesheet)
ball = Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0), 1, 0.1)



while running:
    screen.fill((0, 0, 0))
    tilemap.draw(screen)
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
    ball.freeze_normal_vect()
    ball.moving(tilemap)
    ball.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
