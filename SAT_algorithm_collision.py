import pygame
import math

# Initialisation de pygame
pygame.init()

# Constantes de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Déplacement de formes")
O = [WIDTH // 2, HEIGHT // 2]

# Définition des couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Création des formes
class Triangle :
    def __init__(self,sommet1,sommet2,sommet3,color):
        self.sommet1 = sommet1
        self.sommet2 = sommet2
        self.sommet3 = sommet3
        self.color = color

    def draw_triangle(self):
        pygame.draw.polygon(screen,self.color,[self.sommet1,self.sommet2,self.sommet3])

triangle1 = Triangle(pygame.math.Vector2(HEIGHT),pygame.math.Vector2(100,500),pygame.math.Vector2(400,700),(0,0,0))
rect1 = pygame.Rect(100, 100, 100, 100)  # Rectangle
circle1_center = [300, 300]  # Centre du cercle
circle_radius = 50  # Rayon du cercle
selected_rect = None
dragging = False

done = False


def Axis(A, B):
    """ Retourne un vecteur normalisé perpendiculaire au segment AB """
    dx = B[0] - A[0]
    dy = B[1] - A[1]
    n = [-dy, dx]  # Normal perpendiculaire
    v = math.sqrt(n[0] ** 2 + n[1] ** 2)
    return [n[0] / v, n[1] / v] if v != 0 else [0, 0]  # Évite la division par zéro


def projection(point, axis):
    """ Retourne la projection scalaire d'un point sur un axe donné """
    return point[0] * axis[0] + point[1] * axis[1]


def collision_check(vertices, circle_center, circle_radius): #Order of the vertices do not matter
    """ Vérifie la collision entre un polygone et un cercle via SAT """
    # Liste des axes normaux à tester (les arêtes du polygone)
    axes = []
    for i in range(len(vertices)):
        A = vertices[i]
        B = vertices[(i + 1) % len(vertices)]  # Boucle sur les sommets
        axes.append(Axis(A, B))

    # Tester chaque axe
    for axis in axes:
        # Projection du polygone
        min_poly = max_poly = projection(vertices[0], axis)
        for v in vertices:
            proj = projection(v, axis)
            min_poly = min(min_poly, proj)
            max_poly = max(max_poly, proj)

        # Projection du cercle
        circle_proj = projection(circle_center, axis)
        min_circle = circle_proj - circle_radius
        max_circle = circle_proj + circle_radius

        # Vérifier s'il y a un espace entre les intervalles projetés
        if max_poly < min_circle or max_circle < min_poly:
            return False  # Pas de collision

    return True  # Si aucune séparation n'est trouvée, il y a collision


while not done:
    screen.fill(WHITE)
    triangle1.draw_triangle()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if rect1.collidepoint(event.pos):
                selected_rect = rect1
                dragging = True
            distance = math.hypot(event.pos[0] - circle1_center[0], event.pos[1] - circle1_center[1])
            if distance <= circle_radius:
                selected_rect = "circle"
                dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            selected_rect = None
        elif event.type == pygame.MOUSEMOTION and dragging:
            if selected_rect == rect1:
                rect1.x = event.pos[0] - rect1.width // 2
                rect1.y = event.pos[1] - rect1.height // 2
            elif selected_rect == "circle":
                circle1_center = (event.pos[0], event.pos[1])

    if collision_check([[rect1.x + rect1.width, rect1.y + rect1.height], [rect1.x + rect1.width, rect1.y],
                        [rect1.x, rect1.y], [rect1.x, rect1.y + rect1.height]],
                       circle1_center, circle_radius) or collision_check([[triangle1.sommet1[0],triangle1.sommet1[1]],[triangle1.sommet2[0],triangle1.sommet2[1]],
                                                                         [triangle1.sommet3[0],triangle1.sommet3[1]]],circle1_center,circle_radius):
        pygame.draw.circle(screen, GREEN, circle1_center, circle_radius)
    else:
        pygame.draw.circle(screen, BLUE, circle1_center, circle_radius)

    pygame.draw.rect(screen, RED, rect1)
    pygame.display.flip()

pygame.quit()

