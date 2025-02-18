import pygame,math

pygame.init()
SCREEN_HEIGHT = 720 ; SCREEN_WIDTH = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
active_select = False
in_jump = False
bounce = 0.5
space_pressed = False

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

    def moving(self): #Force is a vector
        self.velocity += pygame.Vector2(0,0.5*self.mass) #apply the weight
        #condtion pour ajouter la friction du sol uniquement
        self.pos += self.velocity
        if self.pos.y >=SCREEN_HEIGHT - self.radius :
            self.pos.y = SCREEN_HEIGHT - self.radius
            self.velocity.y *= -self.retention
            if abs(self.velocity.y) <= bounce:
                self.velocity.y = 0

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

    def get_v0(self,t0,space_pressed):
        while space_pressed :
            pass

class Triangle :
    def __init__(self,sommet1,sommet2,sommet3,color):
        self.sommet1 = sommet1
        self.sommet2 = sommet2
        self.sommet3 = sommet3
        self.color = color

    def draw_triangle(self):
        pygame.draw.polygon(screen,self.color,[self.sommet1,self.sommet2,self.sommet3])


triangle1 = Triangle(pygame.math.Vector2(0,SCREEN_HEIGHT),pygame.math.Vector2(100,500),pygame.math.Vector2(400,700),(255,255,255))
ball = Ball(pygame.math.Vector2(250,250),10,(255,255,255),0.5,0.7,pygame.math.Vector2(0,0),1,10)


running = True
while running:
    ref_v0 = 10
    ball.moving()
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN :
            if event.button == 1:
                if ball.check_select(event.pos) and not active_select:
                    active_select = True
                elif ball.check_select(event.pos) and active_select:
                    active_select = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not in_jump and active_select:
                t0 = pygame.time.get_ticks()
                in_jump = True
                active_select = False
                ball.shoot(ref_v0)
                in_jump = False #so that you cannot jump several times in midair

    if active_select :
        ball.draw_trajectory(ref_v0)
    triangle1.draw_triangle()
    ball.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

"""A faire : -frictions 
-collisions 
-Trouver un moyen d'obtenir v0"""