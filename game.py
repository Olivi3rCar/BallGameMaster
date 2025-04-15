import pygame
import time
import os
from SAT_algorithm_collision import *
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

# ---------------------------
# Classe Ball
# ---------------------------
class Ball:
    """Création de notre balle"""
    def __init__(self, pos, radius, mass, retention, velocity):
        self.pos = pos
        self.radius = radius
        self.mass = mass
        self.retention = retention
        self.velocity = velocity
        self.v0 = None
        self.normal_vector = pygame.math.Vector2(0, 0)
        self.biome = "iceland"  # Utilisé pour déterminer le coefficient de friction
        self.is_shooting = False  # Nouvel attribut pour suivre si la balle est tirée
        self.can_be_selected = True
        self.ice_contact_timer = None  # Timer pour le contact avec la glace
        self.last_ice_tile = None     # Référence au dernier bloc de glace touché

    def draw(self):
        """Dessine la balle à l'écran"""
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.radius)

    def bounce(self):
        """Fait rebondir la balle"""
        normal_velocity_component = self.velocity.dot(self.normal_vector) * self.normal_vector
        reflected_velocity = normal_velocity_component * -(1 + self.retention)

        # Condition pour arrêter les tremblements
        if reflected_velocity.length() < 0.2:  # Limite pour arrêter les tremblements
            return pygame.Vector2(0, 0)
        return reflected_velocity

    def is_normal_good(self, tile):
        """S'assure que nous avons le bon vecteur normal dans la bonne direction"""
        # Normalise le vecteur normal
        self.normal_vector = pygame.Vector2(self.normal_vector).normalize()
        check = double_check(tile.vertices, self.normal_vector)  # Vérifie si on a manqué une pente
        self.normal_vector = pygame.Vector2(check[0], check[1])
        # Test de position
        pos_test = self.pos + 10 * self.normal_vector
        # Vérifie la collision
        if collision_check(tile.vertices, (pos_test.x, pos_test.y), self.radius):  # Vérifie la direction
            self.normal_vector = -self.normal_vector
        return False

    def is_tangent_good(self, tangent_vector):
        """Vérifie également la direction du vecteur tangent"""
        dot_product = self.velocity.dot(tangent_vector)
        # Si le produit scalaire est positif, ils ne sont pas dans des directions opposées, ce qui n'est pas bon
        if dot_product > 0:
            return -tangent_vector
        return tangent_vector

    def weight(self):
        """Calcule le poids"""
        gravity = pygame.Vector2(0, 0.4)  # gravité
        return gravity * self.mass

    def is_on_valid_surface(self):
        """Vérifie si la tuile touchée est une pente (l'angle avec le sol ne doit pas être entre 100 et 80)"""
        slope_angle = self.getting_slope_angle()
        return abs(slope_angle - 90) > 10  # (Pas de frottement contre un mur)

    def apply_friction(self, tangent_vector, normal_force_magnitude):
        """Gère les frottements"""
        if self.is_on_valid_surface():  # On vérifie s'il y a besoin de frottements
            tangential_speed = self.velocity.dot(tangent_vector)
            frictions_coefficients = {"desert": 0.4, "iceland": 0.1, "forest": 0.2}
            coefficient_of_friction = frictions_coefficients[self.biome]

            # Si la vitesse est trop faible, on la réinitialise
            if abs(tangential_speed) < 0.1:
                projection = self.velocity.project(tangent_vector)
                self.velocity -= projection
            else:
                friction_force_magnitude = coefficient_of_friction * normal_force_magnitude
                friction_force = -tangential_speed * tangent_vector.normalize() * friction_force_magnitude
                self.velocity += friction_force

            if self.velocity.dot(tangent_vector) * tangential_speed < 0:
                self.velocity -= tangent_vector * self.velocity.dot(tangent_vector)

    def ice_contact(self, tile):
        """Check if the ball is on a breakable tile and set the timer to destroy it"""
        if tile.index in [27, 28, 29, 30, 31]:  #Check if it's a breakable one
            if tile == self.last_ice_tile:  # If it's the same tile as the previous one
                if self.ice_contact_timer is None:
                    self.ice_contact_timer = time.time()  # Set timer if not already done
                else:
                    difference = time.time() - self.ice_contact_timer
                    if difference > 2:  # 2 secondes
                        tile.broken = 1
                        self.ice_contact_timer = None  # Reset the timer
                        self.last_ice_tile = None     # Reset last block touched
            else:  # If it's a new one
                self.ice_contact_timer = time.time()  # New timer
                self.last_ice_tile = tile            # Set the new tiler
        else:  # Si ce n'est pas un bloc de glace
            self.ice_contact_timer = None  # Reset timer
            self.last_ice_tile = None    # Reset tile

    def moving(self, tilemap, dt):
        """Coordonne toutes les forces sur la balle"""
        weight = self.weight()
        collision_info = self.handle_collision(tilemap)  # Le dictionnaire CONTENANT LES INFOS SUR LES TILES TOUCHÉES
        tangent_vector = pygame.Vector2(0, 1) # Default tangent vector (pointing downwards, which might need adjustment)

        if collision_info:
            for tile_key in collision_info.keys():  # Pour chaque tuile, calcule sa "contribution"
                if tile_key.broken == 0 :
                    self.ice_contact(tile_key)
                    self.normal_vector = collision_info[tile_key][0]
                    self.is_normal_good(tile_key)
                    tangent_vector = pygame.Vector2(-self.normal_vector.y, self.normal_vector.x)
                    # vecteur tangent à la normale
                    penetration = collision_info[tile_key][1]
                    normal_magnitude = self.normal_vector.length()
                    tangent_vector = self.is_tangent_good(tangent_vector)
                    self.repositioning(penetration)
                    # décomposition des forces
                    normal_force = weight.dot(self.normal_vector) * self.normal_vector
                    parallel_force = weight.dot(tangent_vector) * tangent_vector
                    self.velocity += parallel_force + normal_force
                    self.apply_friction(tangent_vector, normal_magnitude)
                    self.velocity += self.bounce()
                    self.is_shooting = False  # Réinitialise le drapeau de tir lors de la collision
                    self.can_be_selected = True  # La balle peut être sélectionnée à nouveau
                else :
                    self.velocity += weight
                    self.normal_vector *= 0
        else:
            self.velocity += weight
            self.normal_vector *= 0

        """Ensemble de conditions pour arrêter la balle si sa vitesse est trop faible"""
        # Limites de vitesse
        if not self.is_on_valid_surface() and collision_info: # Only check if on a valid surface AND there was a collision
            min_speed_threshold = 0.8
        else:
            min_speed_threshold = 0.05

        if self.velocity.length() < min_speed_threshold:
            deceleration_factor = 0.90
            self.velocity *= deceleration_factor
            if abs(self.velocity.dot(tangent_vector)) < 0.01:
                projection = self.velocity.project(tangent_vector)
                self.velocity -= projection

        # Une autre condition d'arrêt
        if abs(self.velocity.x) < 0.01 and abs(self.velocity.y) < 0.1:  # Ajuste ces seuils si nécessaire
            self.velocity = pygame.Vector2(0, 0)

        self.pos += self.velocity * dt * 30  # Indépendance du framerate

    def repositioning(self, penetration):
        """Sort la balle de la tuile touchée en la replaçant un peu plus loin pour qu'elle ne soit pas bloquée"""
        epsilon = 0.1
        self.pos += self.normal_vector * (penetration + epsilon)

    def getting_slope_angle(self):
        """Obtient l'angle de la pente"""
        if self.normal_vector.x == 0:
            return 90 if self.normal_vector.y > 0 else -90  # Pour éviter la division par zéro
        return math.degrees(math.atan2(self.normal_vector.y, self.normal_vector.x))

    def handle_collision(self, tilemap):
        """Crée le dictionnaire des tuiles touchées"""
        closest_collision = None
        max_overlap = 0
        for tile in tilemap.tiles:
            """collision = (vecteur normal de la tuile touchée, profondeur de pénétration) (s'il y a collision)"""
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

    def shoot(self):
        """Déplace la balle selon une trajectoire parabolique"""
        angle = self.get_trajectory_angle()  # Angle entre la position de la souris et le sol
        self.pos += self.normal_vector * 2  # Lève la balle pour qu'elle ne touche pas de tuiles, pour que le mouvement n'interfère pas
        """Voici les formules utilisées pour calculer la vitesse"""
        force = pygame.math.Vector2(self.v0 * (math.cos(math.radians(angle))), -self.v0 * (math.sin(math.radians(angle))))
        # Réinitialise complètement toute vitesse existante
        self.velocity = force / self.mass
        self.is_shooting = True  # Met le drapeau à True lors du tir
        self.can_be_selected = False

    def get_trajectory_angle(self):
        """Obtient l'angle entre la position de la souris et le sol"""
        pos = pygame.mouse.get_pos()
        dx = pos[0] - self.pos.x
        dy = self.pos.y - pos[1]
        if dx == 0:  # Pour éviter la division par zéro
            return 90
        elif dx < 0:
            return 180 - math.degrees(math.atan2(abs(dy), abs(dx)))
        return math.degrees(math.atan2(abs(dy), abs(dx)))

    def check_select(self, pos):
        """Vérifie si on a cliqué sur la balle"""
        return self.can_be_selected and abs(pos[0] - self.pos.x) < 10 and abs(pos[1] - self.pos.y) < 10

    def draw_trajectory(self, v0):
        """Dessine la trajectoire de tir, avec une vitesse initiale de référence"""
        angle_deg = self.get_trajectory_angle()
        angle_rad = math.radians(angle_deg)
        """Ici, on exécute une simulation des positions"""
        pos_x = [v0 * math.cos(angle_rad) * t + self.pos.x for t in range(0, 20, 2)]
        pos_y = [0.5 * 0.5 * t ** 2 - v0 * math.sin(angle_rad) * t + self.pos.y for t in range(0, 20, 2)]
        # On dessine ensuite les points aux coordonnées (x, y)
        for i in range(len(pos_x)):
            pygame.draw.circle(screen, "red", (int(pos_x[i]), int(pos_y[i])), 4)

    def handle_shooting(self, event, active_select):
        """Gère le tir en tenant compte de la barre espace"""
        rate_v0 = 0.02  # Taux d'augmentation de la vitesse initiale
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and active_select and not self.is_shooting:
            self.t0 = pygame.time.get_ticks()  # Début du chronomètre
            self.v0 = 0  # Réinitialisation de la vitesse initiale

        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and self.t0 is not None and active_select and not self.is_shooting:
            duration = pygame.time.get_ticks() - self.t0  # Durée de l'appui sur la barre espace
            self.v0 = min(duration * rate_v0, 15)  # Plafonnement de la vitesse initiale
            self.shoot()  # Tire la balle
            active_select = False  # Désactive la sélection après le tir
            self.t0 = None  # Réinitialise le chronomètre
        return active_select



# ---------------------------
# Charging the items
# ---------------------------
spritesheet = Spritesheet(os.path.join("Sprites png/icetiles.png"), tile_size=32, columns=11) #if not iceland, column = 9
tilemap = Tilemap("tiles_maps/ice_level_4.csv", spritesheet)
ball=Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0))
ball.biome = "iceland" # Set the biome to iceland for this level
image = "Sprites png/bckgroundsand.png" # Use an ice background

def gameplay(screen,ball,tilemap,background_image):
    """Important function that does the loop for a level"""
    game = True
    active_select = False
    previous_time = time.time()
    # ---------------------------
    # Load the background image
    # ---------------------------
    try:
        background_image = pygame.image.load(background_image).convert() #Load the background
        # It's a good idea to convert the image for faster blitting
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        background_image = None # Handle the case where the image fails to load

    while game:
        clock.tick(FPS)
        dt = time.time() - previous_time  # Convert to seconds for frame-rate independence
        previous_time = time.time()
        if background_image is not None:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((0, 0, 0)) # If no background, fill with black
        tilemap.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    for tile in tilemap.tiles :
                        if tile.broken :
                            tile.broken = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and ball.check_select(event.pos) and not ball.is_shooting and ball.can_be_selected:
                    active_select = not active_select
            active_select = ball.handle_shooting(event,active_select)  # Shooting the ball
        if active_select and not ball.is_shooting:
            ball.draw_trajectory(10)
        ball.moving(tilemap, dt)
        ball.draw()
        pygame.display.flip()
    return False # Indicate that the game loop has ended

running = True
while running :
    running = gameplay(screen,ball, tilemap,image)
pygame.quit()