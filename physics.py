#!/usr/bin/env python3
"""
Utilitários de física e geometria computacional para o Sinucadas.
Contém estruturas de dados para pontos e polígonos, testes de orientação
e algoritmos de teste de inclusão ponto em polígono.
"""

from dataclasses import dataclass


@dataclass
class Point:
    """Representa um ponto 2D com coordenadas x e y."""

    x: float
    y: float


@dataclass
class Polygon:
    """Representa um polígono 2D definido por uma lista de vértices."""

    vertices: list[Point]


def on_segment(p: Point, q: Point, r: Point) -> bool:
    """Verifica se o ponto q está contido na bounding box do segmento de reta 'pr'."""
    return min(p.x, r.x) <= q.x <= max(p.x, r.x) and min(p.y, r.y) <= q.y <= max(
        p.y, r.y
    )


def orientation(p: Point, q: Point, r: Point) -> int:
    """Retorna a orientação do trio ordenado (p, q, r): 0 se colinear, 1 se horário, 2 se anti-horário."""
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val == 0:
        return 0
    return 1 if val > 0 else 2


def point_in_polygon(polygon: Polygon, point: Point) -> bool:
    """Lança um raio horizontal do ponto para a direita e conta interseções de arestas (ímpar = dentro)."""
    intersections = 0
    vertices = polygon.vertices
    num_vertices = len(vertices)

    for i in range(num_vertices):
        a = vertices[i]
        b = vertices[(i + 1) % num_vertices]

        if orientation(a, b, point) == 0 and on_segment(a, point, b):
            return True

        if (a.y > point.y) != (b.y > point.y):
            t = (point.y - a.y) / (b.y - a.y)
            x_intersect = a.x + t * (b.x - a.x)
            if x_intersect > point.x:
                intersections += 1

    return intersections % 2 != 0


TABLE_POLYGON = Polygon(
    [
        Point(-0.90, -0.45),
        Point(0.90, -0.45),
        Point(0.90, 0.45),
        Point(-0.90, 0.45),
    ]
)


def check_circle_collision(
    p1: Point, p2: Point, radius: float
) -> tuple[bool, float, float, float]:
    """Verifica colisão entre dois círculos de mesmo raio e retorna (colidiu, dx, dy, distancia)."""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dist_sq = dx * dx + dy * dy
    min_dist = 2.0 * radius
    if 0.0 < dist_sq < (min_dist * min_dist):
        dist = dist_sq**0.5
        return True, dx, dy, dist
    return False, dx, dy, 0.0


def resolve_elastic_collision(
    pos_a: list[float],
    vel_a: list[float],
    pos_b: list[float],
    vel_b: list[float],
    radius: float,
    restitution: float = 0.96,
) -> bool:
    """Resolve a sobreposição geométrica e a troca de momento linear elástico entre duas bolas."""
    dx = pos_b[0] - pos_a[0]
    dy = pos_b[1] - pos_a[1]
    dist_sq = dx * dx + dy * dy
    min_dist = 2.0 * radius

    if dist_sq <= 0.0 or dist_sq >= (min_dist * min_dist):
        return False

    dist = dist_sq**0.5
    nx = dx / dist
    ny = dy / dist

    overlap = min_dist - dist
    pos_a[0] -= 0.5 * overlap * nx
    pos_a[1] -= 0.5 * overlap * ny
    pos_b[0] += 0.5 * overlap * nx
    pos_b[1] += 0.5 * overlap * ny

    rel_vx = vel_a[0] - vel_b[0]
    rel_vy = vel_a[1] - vel_b[1]
    vel_along_normal = rel_vx * nx + rel_vy * ny

    if vel_along_normal <= 0.0:
        return True

    impulse = -(1.0 + restitution) * vel_along_normal * 0.5
    vel_a[0] += impulse * nx
    vel_a[1] += impulse * ny
    vel_b[0] -= impulse * nx
    vel_b[1] -= impulse * ny
    return True


def check_pocket_fall(
    ball_pos: list[float],
    pockets: tuple[tuple[float, float], ...],
    pocket_radius: float,
) -> bool:
    """Verifica se o centro da bola alcançou a área de captura de qualquer uma das caçapas."""
    capture_radius_sq = (pocket_radius * 0.85) ** 2
    bx, by = ball_pos[0], ball_pos[1]
    for px, py in pockets:
        dx = bx - px
        dy = by - py
        if (dx * dx + dy * dy) <= capture_radius_sq:
            return True
    return False


def resolve_cushion_bounce(
    pos: list[float],
    vel: list[float],
    radius: float,
    half_width: float,
    half_height: float,
    restitution: float = 0.85,
) -> bool:
    """Aplica o rebote elástico da bola contra as tabelas delimitadoras da mesa."""
    xmin = -half_width + radius
    xmax = half_width - radius
    ymin = -half_height + radius
    ymax = half_height - radius
    bounced = False

    if pos[0] < xmin:
        pos[0] = xmin
        vel[0] = -vel[0] * restitution
        bounced = True
    elif pos[0] > xmax:
        pos[0] = xmax
        vel[0] = -vel[0] * restitution
        bounced = True

    if pos[1] < ymin:
        pos[1] = ymin
        vel[1] = -vel[1] * restitution
        bounced = True
    elif pos[1] > ymax:
        pos[1] = ymax
        vel[1] = -vel[1] * restitution
        bounced = True

    return bounced


if __name__ == "__main__":
    square = Polygon(
        [Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0, 1.0)]
    )
    assert point_in_polygon(square, Point(0.5, 0.5)) is True
    assert point_in_polygon(square, Point(1.5, 0.5)) is False

    assert point_in_polygon(TABLE_POLYGON, Point(0.0, 0.0)) is True
    assert point_in_polygon(TABLE_POLYGON, Point(1.5, 0.0)) is False

    p_a, v_a = [0.0, 0.0], [1.0, 0.0]
    p_b, v_b = [0.05, 0.0], [0.0, 0.0]
    collided = resolve_elastic_collision(p_a, v_a, p_b, v_b, radius=0.032)
    assert collided is True
    assert v_b[0] > 0.0

    pockets_test = ((0.88, 0.43), (-0.88, -0.43))
    assert check_pocket_fall([0.88, 0.43], pockets_test, 0.055) is True
    assert check_pocket_fall([0.0, 0.0], pockets_test, 0.055) is False

    print("physics.py: testes geométricos e de física elástica passaram com sucesso.")
