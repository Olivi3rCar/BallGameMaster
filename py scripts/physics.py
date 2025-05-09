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
icon = pygame.image.load("golf-icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
running = True

"""Getting the path to the sprites folder"""
path=os.path.abspath(os.path.join("./main.py", os.pardir))
path=str(path)[:-10]+"Sprites png\\"
buttons=pygame.image.load(path+"Buttons.png")
buttons = pygame.transform.scale(buttons, (3 * buttons.get_width(), 3 * buttons.get_height()))
gobackbuttonoff=(0,0,48,48)
gobackbuttonon=(48,0,48,48)
disable_back=False

chargebar = pygame.image.load(path+"Chargebar.png")
chargebar = pygame.transform.scale(chargebar, (3 * chargebar.get_width(), 3 * chargebar.get_height()))
chargebar_rect = [(128*3*i, 0, 128 * 3, 16 * 3) for i in range(17)]

# ---------------------------
# Class Ball
# ---------------------------
def on_button(top_left,bottom_right):
    """Getting the position of the mouse, then checking its position relative to the "hitbox" of the image
    :param top_left: int couple: the position of the top left corner of the image
    :param bottom_right: int couple: the position of the bottom right of the image
    :return: bool: if the mouse is on the image or not
    """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if (top_left[0]<mouse_x<bottom_right[0]) and (top_left[1]<mouse_y<bottom_right[1]):
        return True

class Ball:
    """Creation of our ball"""
    def __init__(self, pos, radius, mass, retention, velocity, biome):
        self.pos = pos
        self.radius = radius
        self.mass = mass
        self.retention = retention
        self.velocity = velocity
        self.t0 = 0
        self.v0 = None
        self.normal_vector = pygame.math.Vector2(0,0)
        self.biome = biome #Used to determine the coefficient of friction
        self.is_shooting = False # New attribute to track if the ball is being shot
        self.can_be_selected = True
        self.ice_contact_timer = None  # Timer pour le contact avec la glace
        self.last_ice_tile = None  # Référence au dernier bloc de glace touché
        self.hit = 0 #Number of strikes

        """Attributs de powerups"""
        self.sticky = False  # init du sticky
        self.fast_fall = False  # init du ff
        self.bouncy = False  # init du bouncy
        self.impact_flash_time = 0
        self.default_retention = retention
        self.initial_pos = pos.copy()  # retient la position d'origine pour le reset (r)

    def toggle_bouncy(self):
        self.bouncy = not self.bouncy
        self.retention = 1.2 if self.bouncy else self.default_retention

    def reset_position(self):
        self.pos = self.initial_pos.copy()
        self.velocity = pygame.Vector2(0, 0)

    def reset_powers(self) :
        """Resets all our power-ups"""
        if self.sticky :
            self.sticky = False
        if self.bouncy :
            self.bouncy = False
        if self.fast_fall :
            self.fast_fall = False
            
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
        max_bounce_speed = self.velocity.length() * 1.90  # Cap la vitesse du rebond pour éviter infinite scale et noclip
        if reflected_velocity.length() > max_bounce_speed:
            reflected_velocity.scale_to_length(max_bounce_speed)
        if reflected_velocity.length() < 0.2:  # pour enlever un rebond/tremblement infini si la valeur est trop basse, on stop net
            return pygame.Vector2(0, 0)
        return reflected_velocity

    def is_normal_good(self,tile):
        """Make sure we have the good normal_vector in the correct direction"""
        # Normalize the normal vector
        self.normal_vector = pygame.Vector2(self.normal_vector).normalize()
        check = double_check(tile.vertices,self.normal_vector) #Check if we missed a slope
        self.normal_vector = pygame.Vector2(check[0],check[1])
        # Test of position
        pos_test = self.pos + 10*self.normal_vector
        # Check for collision
        if collision_check(tile.vertices, (pos_test.x, pos_test.y), self.radius): #Check the direction
            self.normal_vector = -self.normal_vector
        return False

    def is_tangent_good(self, tangent_vector):
        """Also check the direction of the tangent vector"""
        dot_product = self.velocity.dot(tangent_vector)
        # If the dot product is positive, they are not in opposite direction, which is not good
        if dot_product > 0:
            return -tangent_vector
        return tangent_vector

    def weight(self):
        """Calculate the weight"""
        gravity_strength = 0.4
        if self.fast_fall:
            gravity_strength = 2.0  # boosted gravity when fast fall is on
        gravity = pygame.Vector2(0, gravity_strength)
        return gravity * self.mass


        
    def is_on_valid_surface(self):
        """Check if the touched tile is a slope (degree with the ground must not be between 100 and 80)"""
        slope_angle = self.getting_slope_angle()
        return abs(slope_angle-90) > 10  # (No frictions against a wall)

    def apply_friction(self, tangent_vector, normal_force_magnitude):
        """Manages the frictions"""
        if self.is_on_valid_surface(): #We check if there is a need for the frictions
            tangential_speed = self.velocity.dot(tangent_vector)
            frictions_coefficients = {"sand" : 0.4,"ice" : 0.1, "grass" : 0.2}
            coefficient_of_friction = frictions_coefficients[self.biome]

            # If speed is too low, we just reset it
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
                    self.water_contact(tile_key, tilemap)
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
        """Check if the ball is on a breakable tile and set the timer to destroy it"""
        if tile.index in [81, 82, 83, 84, 85]:  #Check if it's a breakable one
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
        else:  # If its not an ice block
            self.ice_contact_timer = None  # Reset timer
            self.last_ice_tile = None     # Reset tile

    def water_contact(self, tile, tilemap):
        if tile.index in [87,91]:
            self.reset_position()
            for tile in tilemap.tiles:
                if tile.broken:
                    tile.broken = 0

    def repositioning(self, penetration):
        """Gets the ball out of the touching tile by replacing it a little further so the ball is not stuck"""
        epsilon = 0.1
        self.pos += self.normal_vector * (penetration + epsilon)

    def getting_slope_angle(self):
        """Gets the angle of the slope"""
        if self.normal_vector.x == 0:
            return 90 if self.normal_vector.y > 0 else -90 #To avoid the division by 0
        return math.degrees(math.atan2(self.normal_vector.y, self.normal_vector.x))


    def handle_collision(self, tilemap):
        """Creates the dictionary of the touching tiles"""
        closest_collision = None
        max_overlap = 0
        for tile in tilemap.tiles:
            """collision = (normal vector of the touching tile, penetration depth) (if there is collision)"""
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
        """Moves the ball in a parabolic trajectory"""
        angle = self.get_trajectory_angle() #Angle between mouse position and ground
        self.pos += self.normal_vector*2 #Raise the ball so it doesn't touch any tiles, so moving does not interfere
        """Here are the formulas used to calculate the velocity"""
        force = pygame.math.Vector2(self.v0*(math.cos(math.radians(angle))), -self.v0 * (math.sin(math.radians(angle))))
        # Reset any existing velocity completely
        self.velocity = force / self.mass
        self.is_shooting = True # Set the flag to True when shooting
        self.can_be_selected = False
        self.hit += 1

    def get_trajectory_angle(self):
        """Get the angle between mouse position and ground"""
        pos = pygame.mouse.get_pos()
        dx = pos[0] - self.pos.x
        dy = self.pos.y - pos[1]
        if dx == 0: #To avoid division by 0
            return 90
        elif dx < 0:
            return 180 - math.degrees(math.atan2(abs(dy), abs(dx)))
        return math.degrees(math.atan2(abs(dy), abs(dx)))

    def check_select(self, pos):
        """Checking if we clicked on the ball"""
        return self.can_be_selected and abs(pos[0] - self.pos.x) < 10 and abs(pos[1] - self.pos.y) < 10

    def draw_trajectory(self, v0):
        """Draw the shooting trajectory, with a initial velocity of reference"""
        angle_deg = self.get_trajectory_angle()
        angle_rad = math.radians(angle_deg)
        """Here we run a simulation of the positions"""
        pos_x = [v0 * math.cos(angle_rad) * t + self.pos.x for t in range(0, 20, 2)]
        pos_y = [0.5 * 0.5 * t ** 2 - v0 * math.sin(angle_rad) * t + self.pos.y for t in range(0, 20, 2)]
        #We draw then the points at coordinates (x,y)
        for i in range(len(pos_x)):
            pygame.draw.circle(screen, "red", (int(pos_x[i]), int(pos_y[i])), 4)

    def handle_shooting(self, event, active_select):
        """Manage the shooting by taking in account the space bar"""
        rate_v0 = 0.02  # Increase rate of the initial velocity
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and active_select and not self.is_shooting:
            self.t0 = pygame.time.get_ticks()  # Start of the chronometer
            self.v0 = 0  # Reset of initial velocity

        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and self.t0 != 0 and active_select and not self.is_shooting:
            duration = pygame.time.get_ticks() - self.t0  # Duration of the pressing of the space bar
            self.v0 = min(duration * rate_v0, 15)  # Capping of the initial velocity
            self.shoot()  # Shoots the ball
            active_select = False # Deactivate selection after shooting
            self.t0 = 0  # Reset the chronometer
        return active_select

    def is_won(self,flag):
        return collision_check(flag.vertices,(self.pos.x,self.pos.y),self.radius)

# ---------------------------
# Charging the items
# ---------------------------
spritesheet = Spritesheet(path + "\\sandtiles.png", tile_size=32, columns=9)
tilemap = Tilemap("..\\tiles_maps\\test_map.csv", spritesheet)
ball=Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0),"forest")
image = "C:/Users/victo/PycharmProjects/BallGameMaster/Sprites png/bckgroundsand.png"

def gameplay(screen,ball,tilemap,background_image):
    """Important function that does the loop for a level"""
    game = True
    active_select = False
    start = pygame.time.get_ticks()
    previous_time = time.time()
    # ---------------------------
    # Load the background image
    # ---------------------------
    while game:
        print(pygame.mouse.get_pos())

        clock.tick(FPS)
        dt = time.time() - previous_time  # Convert to seconds for physics frame-rate independence
        previous_time = time.time()

        # ---------------------------
        # Draw the background first
        # ---------------------------
        if background_image is not None:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((0, 0, 0)) # If no background, fill with black

        tilemap.draw(screen)

        if on_button((0,0),(48,48)):
            screen.blit(buttons, (0,0), gobackbuttonon)
        else:
            screen.blit(buttons, (0,0), gobackbuttonoff)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t: #press t to reset the powers
                    ball.reset_powers()
                if event.key == pygame.K_a:#activation of sticky
                    ball.sticky = not ball.sticky
                if event.key == pygame.K_e: #activation of fast_fall
                    ball.fast_fall = not ball.fast_fall
                if event.key == pygame.K_z:#activation of bouncy
                    ball.toggle_bouncy()
                if event.key == pygame.K_r: #If you press R, all broken tiles will respawn and ball will respawn
                    ball.reset_position()
                    print("down")
                    for tile in tilemap.tiles:
                        if tile.broken:
                            tile.broken = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and ball.check_select(event.pos) and not ball.is_shooting and ball.can_be_selected:
                    active_select = not active_select
                if on_button((0, 0), (48, 48)) and disable_back == False:
                    disable_back = True
                    game=False
            elif event.type == pygame.MOUSEBUTTONUP:
                disable_back = False

            active_select = ball.handle_shooting(event,active_select)  # Shooting the ball
        if active_select and not ball.is_shooting:
            if ball.t0 == 0:
                screen.blit(chargebar, (128,432), chargebar_rect[0])
                ball.draw_trajectory(10)
            else :
                screen.blit(chargebar, (128,432), chargebar_rect[min((pygame.time.get_ticks() - ball.t0)//50, 16)])
                ball.draw_trajectory(min((pygame.time.get_ticks() - ball.t0) * 0.02, 20))
        ball.moving(tilemap, dt)
        ball.draw()
        pygame.display.flip()
    #NEED to return ball.hit and (pygame.get.ticks() - start) which is the timer     
    return ball.hit,(pygame.time.get_ticks() - start)/1000  # Indicate that the game loop has ended

# running = True
# while running :
#     running = gameplay(screen,ball, tilemap,image)
# pygame.quit()
