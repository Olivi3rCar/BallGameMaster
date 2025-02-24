import math

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

