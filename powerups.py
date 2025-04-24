import pygame
import time
import os
from SAT_algorithm_collision import *
from tiles import *
import math

pygame.init()
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 120
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("BallMaster")
icon = pygame.image.load("Sprites/golf-icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()


class Ball:
    def __init__(self, pos, radius, mass, retention, velocity):
        self.pos = pos
        self.initial_pos = pos.copy() #retient la position d'origine pour le reset (r)
        self.radius = radius
        self.mass = mass
        self.default_retention = retention
        self.retention = retention
        self.velocity = velocity
        self.v0 = None
        self.normal_vector = pygame.math.Vector2(0,0)
        self.biome = "desert"
        self.is_shooting = False
        self.can_be_selected = True
        self.ice_contact_timer = None
        self.last_ice_tile = None
        self.sticky = False #init du sticky
        self.fast_fall = False #init du ff
        self.bouncy = False #init du bouncy
        self.impact_flash_time = 0

    def draw(self):
        """Changement de couleur selon powerup"""
        if self.sticky:
            color = (0, 255, 0)
        elif self.bouncy:
            color = (255, 0, 0)
        elif self.fast_fall:
            color = (0, 0, 255)
        else:
            color = (255, 255, 255)
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        if self.fast_fall and pygame.time.get_ticks() - self.impact_flash_time < 100: #effet visu du ff
            pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y + self.radius + 4)), 6, 1)

    def bounce(self):
        """Si sticky activé, la balle ne rebondit pas"""
        if self.sticky:
            return pygame.Vector2(0, 0)
        normal_velocity_component = self.velocity.dot(self.normal_vector) * self.normal_vector
        reflected_velocity = normal_velocity_component * -(1 + self.retention)
        max_bounce_speed = self.velocity.length() * 1.90 # Cap la vitesse du rebond pour éviter infinite scale et noclip
        if reflected_velocity.length() > max_bounce_speed:
            reflected_velocity.scale_to_length(max_bounce_speed)
        if reflected_velocity.length() < 0.2: #pour enlever un rebond/tremblement infini si la valeur est trop basse, on stop net
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
        if dot_product > 0:
            return -tangent_vector
        return tangent_vector

    def weight(self):
        gravity = pygame.Vector2(0, 1.2 if self.fast_fall else 0.4)
        return gravity * self.mass

    def is_on_valid_surface(self):
        slope_angle = self.getting_slope_angle()
        return abs(slope_angle-90) > 10

    def apply_friction(self, tangent_vector, normal_force_magnitude):
        if self.is_on_valid_surface():
            tangential_speed = self.velocity.dot(tangent_vector)
            frictions_coefficients = {"desert": 0.4, "iceland": 0.1, "forest": 0.2}
            coefficient_of_friction = frictions_coefficients[self.biome]

            if abs(tangential_speed) < 0.1:
                projection = self.velocity.project(tangent_vector)
                self.velocity -= projection
            else:
                friction_force_magnitude = coefficient_of_friction * normal_force_magnitude
                friction_force = -tangential_speed * tangent_vector.normalize() * friction_force_magnitude
                self.velocity += friction_force

            if self.velocity.dot(tangent_vector) * tangential_speed < 0:
                self.velocity -= tangent_vector * self.velocity.dot(tangent_vector)

    def moving(self, tilemap, dt):
        weight = self.weight()
        collision_info = self.handle_collision(tilemap)
        tangent_vector = pygame.Vector2(0, 1)

        if collision_info:
            for tile_key in collision_info.keys():
                if self.sticky and tile_key.broken: #désactive sticky si la tile est cassé
                    self.sticky = False
                if tile_key.broken == 0:
                    self.ice_contact(tile_key)
                    self.normal_vector = collision_info[tile_key][0]
                    self.is_normal_good(tile_key)
                    tangent_vector = pygame.Vector2(-self.normal_vector.y, self.normal_vector.x)
                    penetration = collision_info[tile_key][1]
                    normal_magnitude = self.normal_vector.length()
                    tangent_vector = self.is_tangent_good(tangent_vector)
                    self.repositioning(penetration)
                    normal_force = weight.dot(self.normal_vector) * self.normal_vector
                    parallel_force = weight.dot(tangent_vector) * tangent_vector
                    self.velocity += parallel_force + normal_force
                    self.apply_friction(tangent_vector, normal_magnitude)
                    self.velocity += self.bounce()
                    self.is_shooting = False
                    self.can_be_selected = True
                else:
                    self.velocity += weight
                    self.normal_vector *= 0
        else:
            self.velocity += weight
            self.normal_vector *= 0

        if not self.is_on_valid_surface() and collision_info:
            min_speed_threshold = 0.8
        else:
            min_speed_threshold = 0.05

        if self.velocity.length() < min_speed_threshold:
            self.velocity *= 0.90
            if abs(self.velocity.dot(tangent_vector)) < 0.01:
                projection = self.velocity.project(tangent_vector)
                self.velocity -= projection

        if abs(self.velocity.x) < 0.01 and abs(self.velocity.y) < 0.1:
            self.velocity = pygame.Vector2(0, 0)

        if self.sticky and collision_info: #figer la balle lors de collisioon
            self.velocity = pygame.Vector2(0, 0)

        if self.fast_fall and collision_info: #petit effet pour fast fall
            self.impact_flash_time = pygame.time.get_ticks()

        self.pos += self.velocity * dt * 30

    def ice_contact(self, tile):
        if tile.index in [27, 28, 29, 30, 31]:
            if tile == self.last_ice_tile:
                if self.ice_contact_timer is None:
                    self.ice_contact_timer = time.time()
                else:
                    if time.time() - self.ice_contact_timer > 2:
                        tile.broken = 1
                        self.ice_contact_timer = None
                        self.last_ice_tile = None
            else:
                self.ice_contact_timer = time.time()
                self.last_ice_tile = tile
        else:
            self.ice_contact_timer = None
            self.last_ice_tile = None

    def repositioning(self, penetration):
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
        return False

    def shoot(self):
        angle = self.get_trajectory_angle()
        self.pos += self.normal_vector*2
        force = pygame.math.Vector2(self.v0*(math.cos(math.radians(angle))), -self.v0 * (math.sin(math.radians(angle))))
        self.velocity = force / self.mass
        self.is_shooting = True
        self.can_be_selected = False

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
        return self.can_be_selected and abs(pos[0] - self.pos.x) < 10 and abs(pos[1] - self.pos.y) < 10

    def draw_trajectory(self, v0):
        angle_deg = self.get_trajectory_angle()
        angle_rad = math.radians(angle_deg)
        pos_x = [v0 * math.cos(angle_rad) * t + self.pos.x for t in range(0, 20, 2)]
        pos_y = [0.5 * 0.5 * t ** 2 - v0 * math.sin(angle_rad) * t + self.pos.y for t in range(0, 20, 2)]
        for i in range(len(pos_x)):
            pygame.draw.circle(screen, "red", (int(pos_x[i]), int(pos_y[i])), 4)

    def handle_shooting(self, event, active_select):
        rate_v0 = 0.02
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and active_select and not self.is_shooting:
            self.t0 = pygame.time.get_ticks()
            self.v0 = 0
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and self.t0 is not None and active_select and not self.is_shooting:
            duration = pygame.time.get_ticks() - self.t0
            self.v0 = min(duration * rate_v0, 15)
            self.shoot()
            active_select = False
            self.t0 = None
        return active_select

    def toggle_bouncy(self):
        self.bouncy = not self.bouncy
        self.retention = 1.2 if self.bouncy else self.default_retention

    def reset_position(self):
        self.pos = self.initial_pos.copy()
        self.velocity = pygame.Vector2(0, 0)

spritesheet = Spritesheet(os.path.join("Sprites png/icetiles.png"), tile_size=32, columns=11)
tilemap = Tilemap("tiles_maps/ice_level_4.csv", spritesheet)
ball = Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0))
ball.biome = "iceland"
image = "Sprites png/bckgroundsand.png"

def gameplay(screen, ball, tilemap, background_image):
    game = True
    active_select = False
    previous_time = time.time()

    try:
        background_image = pygame.image.load(background_image).convert()
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        background_image = None

    while game:
        clock.tick(FPS)
        dt = time.time() - previous_time
        previous_time = time.time()

        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        tilemap.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and ball.check_select(event.pos) and not ball.is_shooting and ball.can_be_selected:
                    active_select = not active_select
            if event.type == pygame.KEYDOWN: #keybind pour les pouvoirs
                if event.key == pygame.K_a:
                    ball.sticky = not ball.sticky
                if event.key == pygame.K_e:
                    ball.fast_fall = not ball.fast_fall
                if event.key == pygame.K_z:
                    ball.toggle_bouncy()
                if event.key == pygame.K_r:
                    ball.reset_position()
                    for tile in tilemap.tiles:
                        if tile.broken:
                            tile.broken = 0
            active_select = ball.handle_shooting(event, active_select)

        if active_select and not ball.is_shooting:
            ball.draw_trajectory(10)

        ball.moving(tilemap, dt)
        ball.draw()
        pygame.display.flip()

    return False

running = True
while running:
    running = gameplay(screen, ball, tilemap, image)

pygame.quit()
