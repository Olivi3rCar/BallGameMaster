import pygame
import time
from SAT_algorithm_collision import *  # Si tu utilises un module externe, sinon ignorez cette ligne
from tiles import *
# ---------------------------
# Initialization of Pygame window parameters
# ---------------------------
pygame.init()
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 120
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

"""la balle reste coincee sur une pente sans retomber direction du saut + pas toujours les tiles les plus pertinantes
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
        self.shot_state = False
        self.normal_vector = pygame.math.Vector2(0,0)
        self.biome = "iceland"


    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.radius)

    def bounce(self):
        normal_velocity_component = self.velocity.dot(self.normal_vector) * self.normal_vector
        reflected_velocity = normal_velocity_component * -(1 + self.retention)

        # Condition pour arrêter les petits rebonds
        if reflected_velocity.length() < 0.1:  # Seuil pour stopper les rebonds
            return pygame.Vector2(0, 0)
        return reflected_velocity

    def is_normal_good(self,tile): #Make sure we have the good normal_vector MUST MODIFY SO IF WE DO NOT TOUCH A SQUARE, WE ABSOLUTELY NEED ANOTHER VECTOR FOR SLOPE
        # Normalize the normal vector
        self.normal_vector = pygame.Vector2(self.normal_vector).normalize()
        check = double_check(tile.vertices,self.normal_vector)
        self.normal_vector = pygame.Vector2(check[0],check[1])
        # Test position
        pos_test = self.pos + 10*self.normal_vector
        # Check for collision
        if collision_check(tile.vertices, (pos_test.x, pos_test.y), self.radius):
            self.normal_vector = -self.normal_vector
        return False

    def is_tangent_good(self, tangent_vector):
        # Calcul du produit scalaire entre la vitesse et la tangente
        dot_product = self.velocity.dot(tangent_vector)
        # Si le produit scalaire est négatif, la vitesse et la tangente sont opposées, donc on inverse la tangente
        if dot_product > 0:
            return -tangent_vector
        return tangent_vector

    def weight(self):
        gravity = pygame.Vector2(0, 0.4)  # gravity
        return gravity * self.mass

    def is_on_valid_surface(self):
        slope_angle = self.getting_slope_angle()
        return abs(slope_angle-90) > 10  # (No frictions against a wall)

    def apply_friction(self, tangent_vector, normal_force_magnitude):
        if self.is_on_valid_surface():
            tangential_speed = self.velocity.dot(tangent_vector)
            frictions_coefficients = {"desert" : 0.4,"iceland" : 0.1, "forest" : 0.5}
            coefficient_of_friction = frictions_coefficients[self.biome]

            # Si la vitesse le long de la pente est très faible, on l'arrête directement
            if abs(tangential_speed) < 0.1:  # Ajuste ce seuil si nécessaire
                projection = self.velocity.project(tangent_vector)
                self.velocity -= projection
            else:
                # Sinon, on applique la friction normalement
                friction_force_magnitude = coefficient_of_friction * normal_force_magnitude
                friction_force = -tangential_speed * tangent_vector.normalize() * friction_force_magnitude
                self.velocity += friction_force

            # Empêcher le dépassement
            if self.velocity.dot(tangent_vector) * tangential_speed < 0:
                self.velocity -= tangent_vector * self.velocity.dot(tangent_vector)

    def moving(self, tilemap, dt): #condition pour arreter la balle sur pente et lorsqu'elle est immobile
        weight = self.weight()
        collision_info = self.handle_collision(tilemap)
        # The Dictionnary CONTAINING INFOS ABOUT THE TILES THAT ARE TOUCHING
        if collision_info:
            for tile_key in collision_info.keys():
                draw_hitbox(self, tile_key)
                self.normal_vector = collision_info[tile_key][0]
                self.is_normal_good(tile_key)
                tangent_vector = pygame.Vector2(-self.normal_vector.y, self.normal_vector.x)
                # tangent vector to the normal
                penetration = collision_info[tile_key][1]
                normal_magnitude = self.normal_vector.length()
                tangent_vector = self.is_tangent_good(tangent_vector)
                self.repositioning(penetration)
                # forces decomposition
                normal_force = weight.dot(self.normal_vector) * self.normal_vector
                parallel_force = weight.dot(tangent_vector) * tangent_vector
                self.velocity += parallel_force + normal_force
                self.apply_friction(tangent_vector, normal_magnitude)  # PROBLEME AVEC LES FROTTEMENTS
                self.velocity += self.bounce()

            # Seuil de vitesse minimale pour annuler les vitesses faibles
            if not self.is_on_valid_surface():
                min_speed_threshold = 0.8  # Mur ou surface verticale
            else:
                min_speed_threshold = 0.05  # Pente ou sol incliné → permet le glissement

            if self.velocity.length() < min_speed_threshold:
                deceleration_factor = 0.90
                self.velocity *= deceleration_factor
                if abs(self.velocity.dot(tangent_vector)) < 0.01:  # Vérifie la vitesse tangentielle
                    projection = self.velocity.project(tangent_vector)  # Obtient la projection sur la tangente
                    self.velocity -= projection  # Supprime cette composante

            # Nouvelle condition pour arrêter la balle si ses composantes sont très petites
            if abs(self.velocity.x) < 0.01 and abs(self.velocity.y) < 0.1:  # Ajuste ces seuils si nécessaire
                self.velocity = pygame.Vector2(0, 0)

        else:
            self.velocity += weight
            self.normal_vector *= 0
        self.pos += self.velocity * dt * 30  # Framerate independance should now work
        print(self.velocity)

    def repositioning(self, penetration):
        #to reposition the ball, the epsilon is to make sure the ball isn't stuck
        epsilon = 0.1
        self.pos += self.normal_vector * (penetration + epsilon)


    def getting_slope_angle(self):
        if self.normal_vector.x == 0:
            return 90 if self.normal_vector.y > 0 else -90
        return math.degrees(math.atan2(self.normal_vector.y, self.normal_vector.x))

    def handle_collision(self, tilemap):
        closest_collision = None
        max_overlap = 0

        for tile in tilemap.tiles:
            collision = collision_check(tile.vertices, (self.pos.x, self.pos.y), self.radius)

            if collision:
                normal_vector = pygame.Vector2(collision[0]).normalize()
                overlap = collision[1]

                if overlap > max_overlap:
                    max_overlap = overlap
                    closest_collision = (tile, normal_vector, overlap)

        if closest_collision:
            return {closest_collision[0]: (closest_collision[1], closest_collision[2])}
        else:
            return False

    def shoot(self): #Finally work
        angle = self.get_trajectory_angle()
        self.shot_state = True
        self.pos += self.normal_vector*2
        force = pygame.math.Vector2(self.v0*(math.cos(math.radians(angle))), -self.v0 * (math.sin(math.radians(angle))))
        # Reset any existing velocity completely
        self.velocity = force / self.mass

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
            self.v0 = min(duration * rate_v0, 15)  # Limite de puissance
            self.shoot()  # Effectue le tir
            active_select = False
            self.t0 = None  # Réinitialise le chrono





# ---------------------------
# Charging the items
# ---------------------------
spritesheet = Spritesheet(os.path.join("Sprites png/sandtiles.png"), tile_size=32, columns=9)
tilemap = Tilemap("tiles_maps/test_map.csv", spritesheet)
ball=Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0), 1, 0.2)

previous_time = time.time()
while running:
    clock.tick(FPS)
    dt = time.time() - previous_time  # Convert to seconds for frame-rate independence
    previous_time = time.time()

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
    ball.moving(tilemap,dt)
    ball.draw()
    pygame.display.flip()

pygame.quit()
