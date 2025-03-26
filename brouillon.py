import pygame
import math
import csv
import os
from SAT_algorithm_collision import *  # Si tu utilises un module externe, sinon ignorez cette ligne


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




def draw_hitbox(ball,tile) :
    if collision_check(tile.vertices, (ball.pos.x, ball.pos.y), ball.radius) :
        print(f"Tile {tile.index} Hitbox: {tile.vertices}")  # Debugging
        pygame.draw.polygon(screen,"green",tile.vertices)

def highlight_tile(tile):
    pygame.draw.polygon(screen, "green", tile.vertices)

# ---------------------------
# Class Spritesheet
# ---------------------------
class Spritesheet:
    def __init__(self, filename, tile_size=32, columns=9):
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        self.tile_size = tile_size
        self.columns = columns

    def get_tile(self, index):
        x = (index % self.columns) * self.tile_size
        y = (index // self.columns) * self.tile_size
        return self.spritesheet.subsurface((x, y, self.tile_size, self.tile_size))

# ---------------------------
# Class Tile
# ---------------------------
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_index, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.get_tile(tile_index)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x, self.y = x, y
        self.vertices = []
        self.angle = 0
        self.index = tile_index
        self.attribution()
        self.priority = 0

    def attribution(self):
        x, y = self.rect.x, self.rect.y
        tile_vertices = {
            0: [(x + 32, y), (x + 32, y + 32), (x, y + 32),(x, y)],
            1: [(x + 32, y), (x + 32, y + 32), (x, y + 32),(x, y)],
            2: [(x + 32, y), (x + 32, y + 32), (x, y + 32),(x, y)],
            3: [(x + 32, y), (x + 32, y + 32), (x, y + 32),(x, y)],
            4: [(x + 32, y), (x + 32, y + 32), (x, y + 32),(x, y)],
            5: [(x + 32, y + 32), (x, y + 32), (x + 32, y)],
            6: [(x, y + 32),(x + 32, y + 32),(x + 32, y + 17)],
            7: [(x, y + 16),(x, y + 32),(x + 32, y + 32), (x + 32, y)],
            8: [(x + 32, y + 32), (x, y + 32), (x + 32, y + 23)],
            9: [(x + 32, y + 32),  (x+32, y + 12),(x, y + 22),(x, y + 32)],
            10: [(x, y + 11),(x, y + 32),(x + 32, y + 32),(x + 32, y)],
            11: [(x + 32, y + 32), (x + 32, y), (x + 17, y + 32)],
            12: [(x + 32, y + 32), (x + 32, y), (x + 15, y),(x, y + 32)],
            13: [(x + 32, y + 32), (x + 32, y), (x + 23, y + 32)],
            14: [(x + 32, y + 32), (x + 32, y), (x + 22, y),(x + 12, y + 32)],
            15: [(x + 32, y + 32), (x + 32, y), (x + 10, y), (x, y + 32)],
            16: [(x + 32, y + 32), (x, y), (x, y + 32)],
            17: [(x + 32, y + 32), (x, y + 32), (x, y + 17)],
            18: [(x, y), (x, y + 32),(x + 32, y + 32), (x + 32, y + 16)],
            19: [(x + 32, y + 32), (x, y + 32), (x, y + 23)],
            20: [(x, y + 12),(x, y + 32),(x + 32, y + 32), (x + 32, y + 22)],
            21: [(x, y), (x, y + 32),(x + 32, y + 32), (x + 32, y + 11)],
            22: [(x, y), (x, y + 32), (x + 15, y + 32)],
            23: [(x, y), (x, y + 32),(x + 32, y + 32), (x + 17, y)],
            24: [(x, y),(x, y + 32), (x + 10, y + 32)],
            25: [(x, y), (x, y + 32),(x + 21, y + 32),(x + 11, y)],
            26: [(x, y),(x, y+32),(x + 32, y + 32),(x + 23, y)]
        }
        self.vertices = tile_vertices[self.index]
        if self.index not in [0,1,2,3,4] :
            self.priority = 1
        else :
            self.priority = 0


def draw_hitbox(ball,tile) :
    if collision_check(tile.vertices, (ball.pos.x, ball.pos.y), ball.radius) :
        pygame.draw.polygon(screen,"green",tile.vertices)

# ---------------------------
# Class Tilemap
# ---------------------------
class Tilemap:
    def __init__(self, filename, spritesheet):
        self.tile_size = 32
        self.tiles = self.load_tiles(filename, spritesheet)

    def read_csv(self, filename):
        map_data = []
        with open(filename) as data:
            reader = csv.reader(data, delimiter=',')
            for row in reader:
                map_data.append(list(row))
        return map_data

    def load_tiles(self, filename, spritesheet):
        tiles = []
        tile_map = self.read_csv(filename)
        y = 0
        for row in tile_map:
            x = 0
            for tile in row:
                tile_index = int(tile)
                if tile_index != -1:
                    tiles.append(Tile(tile_index, x * self.tile_size, y * self.tile_size, spritesheet))
                x += 1
            y += 1
        return tiles

    def draw(self, surface):
        for tile in self.tiles:
            surface.blit(tile.image, (tile.rect.x, tile.rect.y))

# ---------------------------
# Class Ball
# ---------------------------
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

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.radius)

    def bounce(self, normal_vector):
        normal_velocity_component = self.velocity.dot(normal_vector) * normal_vector
        reflected_velocity = normal_velocity_component * -(1 + self.retention)

        # Condition pour arrêter les petits rebonds
        if reflected_velocity.length() < 0.5:  # Seuil pour stopper les rebonds
            return pygame.Vector2(0, 0)

        return reflected_velocity

    def weight(self):
        gravity = pygame.Vector2(0, 0.4)  # gravity
        return gravity * self.mass

    def frictions(self, normal_vector):
        if self.is_on_valid_surface(normal_vector):
            # Calcul du vecteur tangent
            tangent_vector = pygame.Vector2(-normal_vector.y, normal_vector.x)  # Vecteur tangent au sol

            # Force de friction (proportionnelle à la vitesse actuelle)
            friction_force = -self.velocity.dot(tangent_vector) * self.friction * tangent_vector

            # Vérification si la force de friction est trop grande par rapport à la vitesse actuelle
            if friction_force.length() > self.velocity.length():
                # On applique une petite friction, mais pas plus que la vitesse
                friction_force = -self.velocity

            # Appliquer la friction en diminuant progressivement la vitesse
            # Si la vitesse est faible, on réduit la friction de manière progressive
            if self.velocity.length() < 0.2:  # Si la vitesse est très faible
                friction_force = -self.velocity  # Appliquer une friction plus douce pour finir l'arrêt en douceur

            return friction_force

        return pygame.Vector2(0, 0)

    def is_on_valid_surface(self,normal_vector):
        slope_angle = self.getting_slope_angle(normal_vector)
        return abs(slope_angle-90) > 20  # (No frictions against a wall)

    def moving(self, tilemap):#tile 8 a toujours un mauvais vecteur normal, pareil pour la 9 et les carrés
        weight = self.weight()
        collision_info = self.handle_collision(tilemap) #THE Dictionnary CONTAINING INFOS ABOUT THE TILES THAT ARE TOUCHING
        if collision_info:
            for tile_key in collision_info.keys():
                draw_hitbox(self,tile_key)
                normal_vector = collision_info[tile_key][0]



                tangent_vector = pygame.Vector2(-normal_vector.y, normal_vector.x)  # tangeant vector to the normal
                penetration = collision_info[tile_key][1]
                self.repositioning(normal_vector, penetration)
                # forces decomposition
                normal_force = weight.dot(normal_vector) * normal_vector
                parallel_force = weight.dot(tangent_vector) * tangent_vector
                self.velocity += -parallel_force + normal_force
                self.velocity += self.bounce(normal_vector)
                self.velocity += self.frictions(normal_vector) #PROBLEME AVEC LES FROTTEMENTS
                if abs(self.velocity.y) < 0.21:  # Si la vitesse verticale est trop faible
                    self.velocity.y = 0  # On annule la vitesse verticale, mais on conserve la vitesse horizontale
                    # Appliquer une petite composante de mouvement même sur une pente très douce
                    if abs(self.velocity.x) < 0.01:  # Si la vitesse horizontale est très faible
                        self.velocity.x = 0  # Arrêt total, on peut aussi ajuster ce seuil pour plus de fluidité
                print("Collision detected",tile_key.index,normal_vector, "Current speed :",self.velocity)
        else:
            self.velocity += weight


        self.pos += self.velocity


    def repositioning(self, normal_vector, penetration):
        #to reposition the ball, the epsilon is to make sure the ball isn't stuck
        epsilon = 0.1
        self.pos += normal_vector * (penetration + epsilon)



    def getting_slope_angle(self, normal_vector):
        if normal_vector.x == 0:
            return 90 if normal_vector.y > 0 else -90
        return math.degrees(math.atan2(normal_vector.y, normal_vector.x))

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
        force = pygame.math.Vector2(self.v0 * math.cos(math.radians(angle)), self.v0 * math.sin(math.radians(angle)))
        self.velocity += force / self.mass


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
            self.v0 = min(duration * rate_v0, 20)  # Limite de puissance
            self.shoot()  # Effectue le tir
            active_select = False
            self.t0 = None  # Réinitialise le chrono


# ---------------------------
# Charging the items
# ---------------------------
spritesheet = Spritesheet(os.path.join("Sprites png/sandtiles.png"), tile_size=32, columns=9)
tilemap = Tilemap("tiles_maps/test_map.csv", spritesheet)
ball = Ball(pygame.math.Vector2(400, 150), 7, 0.4, 0.6, pygame.math.Vector2(0, 0), 1, 0.1)



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
    ball.moving(tilemap)
    ball.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
