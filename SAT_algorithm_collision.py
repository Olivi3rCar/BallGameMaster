import math
"""This is my version of the Separation Axis Theorem,
modified to work only with a circle and a polygon, we do not need anything else"""

def Axis(A, B):
    """Returns a normalized normal vector of the segment AB"""
    dx, dy = B[0] - A[0], B[1] - A[1]
    n = [-dy, dx]  # Normale perpendiculaire
    v = math.hypot(n[0], n[1])  # Calcul de la norme (plus stable que sqrt)
    return [n[0] / v, n[1] / v] if v != 0 else [0, 0]


def projection(point, axis):
    """Returns the projection of a scalar on an axis"""
    return point[0] * axis[0] + point[1] * axis[1]


def collision_check(vertices, circle_center, circle_radius):
    """Check the collisions between a convex polygon and a circle"""
    axes = []
    min_overlap = float('inf')
    collision_normal = None
    axis_to_look = None

    #Generate our list of potential axis
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
        tolerance = 0.5
        if max_poly < min_circle - tolerance or max_circle + tolerance < min_poly:
            return False  # Pas de collision sur cet axe

        overlap = min(max_poly - min_circle, max_circle - min_poly)
        if overlap < min_overlap :
            min_overlap = overlap
            collision_normal = axis
        if abs(overlap - min_overlap) < min_overlap * 0.7:
            if (abs(axis[0]) < 0.99) and (abs(axis[1]) < 0.99):
                axis_to_look = axis #WE need to store the only vector who is not +-1,0 or 0,-+1, in case we have a ball so fast it touches 2 edges
                overlap_to_look = overlap

    if axis_to_look :
        return axis_to_look,overlap_to_look
    if collision_normal is not None:
        return collision_normal, min_overlap
    return False

def double_check(vertices,previous_normal):
    """If we have a normal vector that is a unit one for a slope tile, which is clearly a bug"""
    axes = []
    for i in range(len(vertices)):
        A = vertices[i]
        B = vertices[(i + 1) % len(vertices)]
        axis = Axis(A, B)
        axes.append(axis)
    for i in range(len(axes)) :
        if axes[i][0] not in [0,1,-1] or axes[i][1] not in [0,1,-1] :
            return axes[i]
    return previous_normal


