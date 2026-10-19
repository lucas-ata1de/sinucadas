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
    def _test_physics_module() -> None:
        import math

        # 1. 2D dot product and vector math
        assert _dot_2d((1.0, 2.0), (3.0, 4.0)) == 11.0
        assert _dot_2d((0.0, 0.0), (5.0, 5.0)) == 0.0

        # 2. Elastic collision: head-on impact
        p_a, v_a = [0.0, 0.0], [1.0, 0.0]
        p_b, v_b = [0.05, 0.0], [0.0, 0.0]
        collided = resolve_elastic_collision(p_a, v_a, p_b, v_b, radius=0.032)
        assert collided is True
        assert v_b[0] > 0.0
        assert v_a[0] < 1.0

        # 3. Elastic collision: distant balls (no collision)
        p_far_a, v_far_a = [0.0, 0.0], [1.0, 0.0]
        p_far_b, v_far_b = [0.5, 0.0], [0.0, 0.0]
        assert resolve_elastic_collision(p_far_a, v_far_a, p_far_b, v_far_b, radius=0.032) is False

        # 4. Elastic collision: coincident centers (singularity / zero distance guard)
        p_zero_a, v_zero_a = [0.0, 0.0], [0.0, 0.0]
        p_zero_b, v_zero_b = [0.0, 0.0], [0.0, 0.0]
        assert resolve_elastic_collision(p_zero_a, v_zero_a, p_zero_b, v_zero_b, radius=0.032) is False

        # 5. Elastic collision: balls already moving apart
        p_sep_a, v_sep_a = [0.0, 0.0], [-1.0, 0.0]
        p_sep_b, v_sep_b = [0.05, 0.0], [1.0, 0.0]
        assert resolve_elastic_collision(p_sep_a, v_sep_a, p_sep_b, v_sep_b, radius=0.032) is True
        assert v_sep_a[0] == -1.0  # impulse not applied if moving apart

        # 6. Cushion bounce: inside bounds (no bounce)
        p_in, v_in = [0.0, 0.0], [0.5, 0.5]
        assert resolve_cushion_bounce(p_in, v_in, radius=0.032, half_bounds=(0.90, 0.45)) is False
        assert p_in == [0.0, 0.0] and v_in == [0.5, 0.5]

        # 7. Cushion bounce: X and Y boundaries with restitution
        p_bx, v_bx = [0.95, 0.0], [2.0, 0.0]
        bounced_x = resolve_cushion_bounce(
            p_bx, v_bx, radius=0.032, half_bounds=(0.90, 0.45), restitution=0.5
        )
        assert bounced_x is True
        assert math.isclose(p_bx[0], 0.90 - 0.032)
        assert math.isclose(v_bx[0], -1.0)

        p_by, v_by = [0.0, 0.45], [0.0, 2.0]
        bounced_y = resolve_cushion_bounce(
            p_by, v_by, radius=0.032, half_bounds=(0.90, 0.45), restitution=0.5
        )
        assert bounced_y is True
        assert math.isclose(p_by[1], 0.45 - 0.032)
        assert math.isclose(v_by[1], -1.0)

        # 8. Pocket fall detection
        pockets_test = ((0.88, 0.43), (-0.88, -0.43))
        assert check_pocket_fall([0.88, 0.43], pockets_test, 0.055) is True
        assert check_pocket_fall([0.0, 0.0], pockets_test, 0.055) is False

        print("physics.py: elastic collision, cushion restitution, and pocket fall tests passed successfully.")

    _test_physics_module()
