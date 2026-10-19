#!/usr/bin/env python3
"""
Motor de física e dinâmica elástica para o Sinucadas.
Contém resolução de colisão perfeitamente elástica entre bolas,
rebote contra as tabelas da mesa e detecção de encaçapamento.
"""

from collections.abc import Sequence


def _dot_2d(v1: Sequence[float], v2: Sequence[float]) -> float:
    """Calcula o produto escalar entre dois vetores bidimensionais."""
    return v1[0] * v2[0] + v1[1] * v2[1]


def _displacement(
    p1: Sequence[float], p2: Sequence[float]
) -> tuple[tuple[float, float], float]:
    """Calcula o vetor deslocamento delta de p1 para p2 e o quadrado da distância euclidiana."""
    delta = (p2[0] - p1[0], p2[1] - p1[1])
    return delta, _dot_2d(delta, delta)


def _bounce_1d(
    pos: list[float], vel: list[float], axis: int, bounds: Sequence[float], restitution: float
) -> bool:
    """Aplica colisão elástica unidimensional em um eixo delimitador com coeficiente de restituição."""
    min_val, max_val = bounds[0], bounds[1]
    if pos[axis] < min_val:
        pos[axis] = min_val
        vel[axis] = -vel[axis] * restitution
        return True
    if pos[axis] > max_val:
        pos[axis] = max_val
        vel[axis] = -vel[axis] * restitution
        return True
    return False


def resolve_elastic_collision(
    pos_a: list[float],
    vel_a: list[float],
    pos_b: list[float],
    vel_b: list[float],
    radius: float,
    restitution: float = 0.96,
) -> bool:
    """Resolve a sobreposição geométrica e a troca de momento linear elástico entre duas bolas."""
    delta, dist_sq = _displacement(pos_a, pos_b)
    min_dist = 2.0 * radius

    if dist_sq <= 0.0 or dist_sq >= (min_dist * min_dist):
        return False

    dist = dist_sq**0.5
    normal = (delta[0] / dist, delta[1] / dist)

    overlap = min_dist - dist
    correction = 0.5 * overlap
    pos_a[0] -= correction * normal[0]
    pos_a[1] -= correction * normal[1]
    pos_b[0] += correction * normal[0]
    pos_b[1] += correction * normal[1]

    rel_vel = (vel_a[0] - vel_b[0], vel_a[1] - vel_b[1])
    vel_along_normal = _dot_2d(rel_vel, normal)

    if vel_along_normal <= 0.0:
        return True

    impulse = -(1.0 + restitution) * vel_along_normal * 0.5
    vel_a[0] += impulse * normal[0]
    vel_a[1] += impulse * normal[1]
    vel_b[0] -= impulse * normal[0]
    vel_b[1] -= impulse * normal[1]
    return True


def check_pocket_fall(
    ball_pos: Sequence[float], pockets: tuple[tuple[float, float], ...], pocket_radius: float
) -> bool:
    """Verifica se o centro da bola alcançou a área de captura de qualquer uma das caçapas."""
    capture_limit_sq = (pocket_radius * 0.85) ** 2
    return any(_displacement(ball_pos, pocket)[1] <= capture_limit_sq for pocket in pockets)


def resolve_cushion_bounce(
    pos: list[float],
    vel: list[float],
    radius: float,
    half_bounds: Sequence[float] = (0.90, 0.45),
    restitution: float = 0.85,
) -> bool:
    """Aplica o rebote elástico da bola contra as tabelas delimitadoras da mesa."""
    bounced_x = _bounce_1d(
        pos, vel, 0, (-half_bounds[0] + radius, half_bounds[0] - radius), restitution
    )
    bounced_y = _bounce_1d(
        pos, vel, 1, (-half_bounds[1] + radius, half_bounds[1] - radius), restitution
    )
    return bounced_x or bounced_y


if __name__ == "__main__":
    p_a, v_a = [0.0, 0.0], [1.0, 0.0]
    p_b, v_b = [0.05, 0.0], [0.0, 0.0]
    collided = resolve_elastic_collision(p_a, v_a, p_b, v_b, radius=0.032)
    assert collided is True
    assert v_b[0] > 0.0

    bounced_x = resolve_cushion_bounce(
        [0.95, 0.0], [1.0, 0.0], radius=0.032, half_bounds=(0.90, 0.45)
    )
    assert bounced_x is True

    bounced_y = resolve_cushion_bounce(
        [0.0, 0.45], [0.0, 1.0], radius=0.032, half_bounds=(0.90, 0.45)
    )
    assert bounced_y is True

    pockets_test = ((0.88, 0.43), (-0.88, -0.43))
    assert check_pocket_fall([0.88, 0.43], pockets_test, 0.055) is True
    assert check_pocket_fall([0.0, 0.0], pockets_test, 0.055) is False

    assert _dot_2d((1.0, 2.0), (3.0, 4.0)) == 11.0

    print("physics.py: elastic collision, cushions, and pocket fall tests passed successfully.")
