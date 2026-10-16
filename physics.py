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
    return min(p.x, r.x) <= q.x <= max(p.x, r.x) and min(p.y, r.y) <= q.y <= max(p.y, r.y)


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


if __name__ == "__main__":
    square = Polygon([Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0, 1.0)])
    assert point_in_polygon(square, Point(0.5, 0.5)) is True
    assert point_in_polygon(square, Point(1.5, 0.5)) is False
    print("physics.py: testes geométricos passaram com sucesso.")
