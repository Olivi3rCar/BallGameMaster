import pygame
import time
from SAT_algorithm_collision import *  # Si tu utilises un module externe, sinon ignorez cette ligne
from tiles import *
import os
import math

# ---------------------------
# Initialization of Pygame window parameters
# ---------------------------
pygame.init()
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("BallMaster")
icon = pygame.image.load("Sprites/golf-icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
running = True
active_select = False
in_jump = False
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
        self.initial_pos = pos.copy()
        self.radius = radius
        self.mass = mass
        self.default_retention = retention
        self.retention = retention
        self.velocity = velocity
        self.id = id
        self.friction = friction
        self.v0 = None
        self.shot_state = False
        self.normal_vector = pygame.math.Vector2(0,0)
        self.sticky = False
        self.fast_fall = False
        self.bouncy = False
        self.impact_flash_time = 0

    def draw(self):
        if self.sticky:
            color = (0, 255, 0)
        elif self.bouncy:
            color = (255, 0, 0)
        elif self.fast_fall:
            color = (0, 0, 255)
        else:
            color = (255, 255, 255)
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), self.radius)

        if self.fast_fall and pygame.time.get_ticks() - self.impact_flash_time < 100:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y + self.radius + 4)), 6, 1)

    def bounce(self):
        if self.sticky:
            return pygame.Vector2(0, 0)
        normal_velocity_component = self.velocity.dot(self.normal_vector) * self.normal_vector
        reflected_velocity = normal_velocity_component * -(1 + self.retention)
        if reflected_velocity.length() < 0.1:
            return pygame.Vector2(0, 0)
        return reflected_velocity

    def is_normal_good(self,tile):
        self.normal_vector = pygame.Vector2(self.normal_vector).normalize()
        check = double_check(tile.vertices,self.normal_vector)
        self.normal_vector = pygame.Vector2(check[0],check[1])
        pos_test = self.pos + 10*self.normal_vector
        if collision_check(tile.vertices, (pos_test.x, pos_test.y), self.radius):
            self.normal_vector = -self.normal_vector
        return False

    def is_tangent_good(self, tangent_vector):
        dot_product = self.velocity.dot(tangent_vector)
        if dot_product < 0:
            return -tangent_vector
        return tangent_vector

    def weight(self):
        gravity_strength = 0.4 if not self.fast_fall else 1.2
        gravity = pygame.Vector2(0, gravity_strength)
        return gravity * self.mass

    def is_on_valid_surface(self):
        slope_angle = self.getting_slope_angle()
        return abs(slope_angle-90) > 10

    def apply_friction(self, tangent_vector):
        if self.is_on_valid_surface():
            friction_force = -self.velocity.dot(tangent_vector) * self.friction * tangent_vector
            if self.velocity.length() < 0.3:
                smoothing_factor = self.velocity.length() / 0.3
                friction_force = -self.velocity * smoothing_factor * 0.7
            if friction_force.length() > self.velocity.length():
                friction_force = -self.velocity * 0.9
            self.velocity += friction_force

    def moving(self, tilemap,dt):
        weight = self.weight()
        collision_info = self.handle_collision(tilemap)
        if collision_info:
            for tile_key in collision_info.keys():
                draw_hitbox(self,tile_key)
                self.normal_vector = collision_info[tile_key][0]
                self.is_normal_good(tile_key)
                tangent_vector = pygame.Vector2(-self.normal_vector.y, self.normal_vector.x)
                penetration = collision_info[tile_key][1]
                tangent_vector = self.is_tangent_good(tangent_vector)
                self.repositioning(penetration)
                normal_force = weight.dot(self.normal_vector) * self.normal_vector
                parallel_force = weight.dot(tangent_vector) * tangent_vector

                if not self.sticky:
                    self.velocity += -parallel_force + normal_force
                    self.apply_friction(tangent_vector)
                    self.velocity += self.bounce()

                if not self.is_on_valid_surface():
                    min_speed_threshold = 0.8
                else:
                    min_speed_threshold = 0.05

                if self.velocity.length() < min_speed_threshold:
                    self.velocity *= 0.95
                    if self.velocity.length() < 0.01:
                        self.velocity = pygame.Vector2(0, 0)

            if self.sticky:
                self.velocity = pygame.Vector2(0, 0)

            if self.fast_fall:
                self.impact_flash_time = pygame.time.get_ticks()

        else:
            self.velocity += weight

        self.pos += self.velocity*dt*70

    def repositioning(self, penetration):
        epsilon = 0.1
        self.pos += self.normal_vector * (penetration + epsilon)

    def getting_slope_angle(self):
        if self.normal_vector.x == 0:
            return 90 if self.normal_vector.y > 0 else -90
        return math.degrees(math.atan2(self.normal_vector.y, self.normal_vector.x))

    def handle_collision(self, tilemap):
        collision_tiles = {}
        ANGLE_THRESHOLD = 10
        EDGE_ANGLE_THRESHOLD = 75

        for tile in tilemap.tiles:
            collision = collision_check(tile.vertices, (self.pos.x, self.pos.y), self.radius)
            if collision:
                normal_vector = pygame.Vector2(collision[0]).normalize()
                overlap = collision[1]
                added = False
                for existing_tile, (existing_normal, existing_overlap) in list(collision_tiles.items()):
                    angle_between = abs(existing_normal.angle_to(normal_vector))
                    if angle_between < ANGLE_THRESHOLD:
                        if overlap > existing_overlap:
                            collision_tiles[existing_tile] = (normal_vector, overlap)
                        added = True
                        break
                    elif angle_between > EDGE_ANGLE_THRESHOLD:
                        if overlap > existing_overlap:
                            collision_tiles.clear()
                            collision_tiles[tile] = (normal_vector, overlap)
                        added = True
                        break
                if not added and len(collision_tiles) < 2:
                    collision_tiles[tile] = (normal_vector, overlap)

        return collision_tiles if collision_tiles else False

    def shoot(self):
        angle = self.get_trajectory_angle()
        self.shot_state = True
        self.pos += self.normal_vector*2
        force = pygame.math.Vector2(self.v0*(math.cos(math.radians(angle))), -self.v0 * (math.sin(math.radians(angle))))
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
        global active_select
        rate_v0 = 0.02
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.t0 = pygame.time.get_ticks()
            self.v0 = 0
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and self.t0 is not None and active_select:
            duration = pygame.time.get_ticks() - self.t0
            self.v0 = min(duration * rate_v0, 10)
            self.shoot()
            active_select = False
            self.t0 = None

    def toggle_bouncy(self):
        self.bouncy = not self.bouncy
        self.retention = 1.2 if self.bouncy else self.default_retention

    def reset_position(self):
        self.pos = self.initial_pos.copy()
        self.velocity = pygame.Vector2(0, 0)


# ---------------------------
# Charging the items
# ---------------------------
spritesheet = Spritesheet(os.path.join("Sprites png/sandtiles.png"), tile_size=32, columns=9)
tilemap = Tilemap("tiles_maps/test_map.csv", spritesheet)
ball = Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0), 1, 0.2)

previous_time = time.time()
while running:
    clock.tick(FPS)
    dt = time.time() - previous_time
    previous_time = time.time()

    screen.fill((0, 0, 0))
    tilemap.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and ball.check_select(event.pos):
                active_select = not active_select
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                ball.sticky = not ball.sticky
            if event.key == pygame.K_e:
                ball.fast_fall = not ball.fast_fall
            if event.key == pygame.K_z:
                ball.toggle_bouncy()
            if event.key == pygame.K_r:
                ball.reset_position()
        in_jump = True
        ball.handle_shooting(event)
    if active_select:
        ball.draw_trajectory(10)
    ball.moving(tilemap, dt)
    ball.draw()
    pygame.display.flip()

pygame.quit()
