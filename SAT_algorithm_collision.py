import math

def Axis(A, B):
    #return a normal vector of the edge AB
    dx = B[0] - A[0]
    dy = B[1] - A[1]
    n = [-dy, dx]
    v = math.sqrt(n[0] ** 2 + n[1] ** 2)
    return [n[0] / v, n[1] / v] if v != 0 else [0, 0]


def projection(point, axis):
    #return the projection of a given point on a given axis
    return point[0] * axis[0] + point[1] * axis[1]


def collision_check(vertices, circle_center, circle_radius): #Order of the vertices does not matter
    # List of all axis to check
    axes = []
    min_overlap = float('inf')  # To get the smallest 'touching' axis
    collision_normal = None
    for i in range(len(vertices)):
        A = vertices[i]
        B = vertices[(i + 1) % len(vertices)]  # Boucle sur les sommets
        axes.append(Axis(A, B))

    # Test each axis
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
            return False  # No collision

        overlap = min(max_poly - min_circle, max_circle - min_poly)
        if overlap < min_overlap:
            min_overlap = overlap
            collision_normal = axis

    return True,collision_normal  # If no separation found, there is collision, gives back the vector

