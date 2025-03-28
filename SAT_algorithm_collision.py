import math

def Axis(A, B):
    """Retourne un vecteur normalisé perpendiculaire au segment AB (normale)."""
    dx, dy = B[0] - A[0], B[1] - A[1]
    n = [-dy, dx]  # Normale perpendiculaire
    v = math.hypot(n[0], n[1])  # Calcul de la norme (plus stable que sqrt)
    return [n[0] / v, n[1] / v] if v != 0 else [0, 0]


def projection(point, axis):
    """Retourne la projection scalaire d'un point sur un axe donné."""
    return point[0] * axis[0] + point[1] * axis[1]


def collision_check(vertices, circle_center, circle_radius):
    axes = []
    min_overlap = float('inf')
    collision_normal = None

    for i in range(len(vertices)):
        A = vertices[i]
        B = vertices[(i + 1) % len(vertices)]
        axis = Axis(A, B)
        axes.append(axis)

    for axis in axes:
        min_poly = max_poly = projection(vertices[0], axis)
        for v in vertices:
            proj = projection(v, axis)
            min_poly = min(min_poly, proj)
            max_poly = max(max_poly, proj)

        circle_proj = projection(circle_center, axis)
        min_circle = circle_proj - circle_radius
        max_circle = circle_proj + circle_radius

        # Avoid false collisions
        tolerance = 0.3
        if max_poly < min_circle - tolerance or max_circle + tolerance < min_poly:
            return False  # Pas de collision sur cet axe

        overlap = min(max_poly - min_circle, max_circle - min_poly)
        if overlap < min_overlap:
            min_overlap = overlap
            collision_normal = axis

    if collision_normal is not None:
        return collision_normal, min_overlap
    return False



