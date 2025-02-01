import pygame, sys

# Initialisation de pygame et de la fenêtre
pygame.init()
screen_width, screen_height = 900, 500
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("BallMaster")

# Chargement de l'icône
icon = pygame.image.load("Sprites/golf-icon.png")
pygame.display.set_icon(icon)

# Définition des objets
ball = pygame.Rect(screen_width // 4, screen_height // 5, 10, 10)  # Balle
ground = pygame.Rect(0, screen_height * 3 / 4, screen_width, screen_height / 4)  # Sol

# Variables de physique
velocity = {"y": 0,"x": 0}  # Dictionnaire pour gérer la vitesse en y
gravity = 0.5  # Force de gravité
is_jumping = False

def apply_physics(obj, velocity, gravity, ground):
    global is_jumping

    if is_jumping :

        obj.x += velocity["x"]
        obj.y += velocity["y"]
        velocity["y"] = -0.5*gravity


    else :
        velocity["y"] += gravity  # Appliquer la gravité à la vitesse
        obj.y += velocity["y"]  # Appliquer la vitesse à la position

    # Collision avec le sol
    if obj.bottom >= ground.y:
        obj.bottom = ground.y  # Ajuster la position
        velocity["y"] = 0  # Arrêter la vitesse de chute
        velocity["x"] = 0  # Arrêter le déplacement en x
        is_jumping = False  # Terminer le saut

running = True
while running:
    screen.fill(GREEN)
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN :
            if event.key == pygame.K_SPACE :
                is_jumping = True
                velocity["x"] = 5
                velocity["y"] = -10
    # Appliquer la physique à la balle
    apply_physics(ball, velocity, gravity, ground)
    # Dessiner les objets
    pygame.draw.rect(screen, WHITE, ball, 0, 5)  # Dessiner la balle
    pygame.draw.rect(screen, BLACK, ground)  # Dessiner le sol

    pygame.time.delay(20)  # Réduire la vitesse d'exécution
    pygame.display.update()

pygame.quit()

