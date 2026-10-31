#!/usr/bin/env python3
"""
Motor de física 2D e geometria computacional para o Sinucadas (Atividade 03).
Implementa colisão elástica bola-bola com conservação de momento linear,
rebote nas tabelas com abertura nas bocas das caçapas, detecção de encaçapamento
com funil gravitacional nas bordas e raycast analítico de mira (Ghost Ball).
"""

from collections.abc import Sequence
from math import cos, sin, sqrt

DEFAULT_TABLE_BOUNDS: tuple[float, float] = (0.90, 0.45)
DEFAULT_BALL_RESTITUTION: float = 0.96
DEFAULT_CUSHION_RESTITUTION: float = 0.85
DEFAULT_POCKET_RADIUS: float = 0.055

POCKET_CAPTURE_RATIO: float = 0.92
POCKET_RIM_RATIO: float = 1.35
POCKET_GRAVITY_PULL: float = 1.8
POCKET_MOUTH_CLEARANCE: float = 1.15
POCKET_OUTER_RATIO: float = 0.5
POCKET_CUSHION_RESTITUTION_FACTOR: float = 0.6
RAYCAST_MAX_DISTANCE: float = 1.90


def dot_2d(v1: Sequence[float], v2: Sequence[float]) -> float:
    """Calcula o produto escalar entre dois vetores bidimensionais."""
    return v1[0] * v2[0] + v1[1] * v2[1]


def displacement(
    p1: Sequence[float], p2: Sequence[float]
) -> tuple[tuple[float, float], float]:
    """Calcula o vetor deslocamento de p1 para p2 e o quadrado da distância euclidiana."""
    delta = (p2[0] - p1[0], p2[1] - p1[1])
    return delta, dot_2d(delta, delta)


def _is_near_pocket_mouth(
    pos: Sequence[float],
    pockets: tuple[tuple[float, float], ...],
    jaw_radius: float,
) -> bool:
    """Verifica se a posição da bola está na abertura (boca) de alguma caçapa."""
    jaw_sq = jaw_radius * jaw_radius
    return any(displacement(pos, pocket)[1] <= jaw_sq for pocket in pockets)


def _bounce_1d(
    pos: list[float],
    vel: list[float],
    axis: int,
    bounds: Sequence[float],
    restitution: float,
) -> bool:
    """Aplica reflexão unidimensional contra os limites de um eixo com restituição."""
    min_val, max_val = bounds[0], bounds[1]
    if pos[axis] < min_val:
        pos[axis] = min_val
        vel[axis] = abs(vel[axis]) * restitution
        return True
    if pos[axis] > max_val:
        pos[axis] = max_val
        vel[axis] = -abs(vel[axis]) * restitution
        return True
    return False


def resolve_elastic_collision(
    pos_a: list[float],
    vel_a: list[float],
    pos_b: list[float],
    vel_b: list[float],
    radius: float,
    restitution: float = DEFAULT_BALL_RESTITUTION,
) -> bool:
    """Resolve a sobreposição geométrica e a troca de momento linear elástico entre duas bolas."""
    delta, dist_sq = displacement(pos_a, pos_b)
    min_dist = 2.0 * radius

    if dist_sq <= 1e-12 or dist_sq >= (min_dist * min_dist):
        return False

    dist = sqrt(dist_sq)
    normal = (delta[0] / dist, delta[1] / dist)

    overlap = min_dist - dist
    correction = 0.5 * overlap
    pos_a[0] -= correction * normal[0]
    pos_a[1] -= correction * normal[1]
    pos_b[0] += correction * normal[0]
    pos_b[1] += correction * normal[1]

    rel_vel = (vel_a[0] - vel_b[0], vel_a[1] - vel_b[1])
    vel_along_normal = dot_2d(rel_vel, normal)

    if vel_along_normal <= 0.0:
        return True

    impulse = -(1.0 + restitution) * vel_along_normal * 0.5
    vel_a[0] += impulse * normal[0]
    vel_a[1] += impulse * normal[1]
    vel_b[0] -= impulse * normal[0]
    vel_b[1] -= impulse * normal[1]
    return True


def check_pocket_fall(
    ball_pos: Sequence[float],
    pockets: tuple[tuple[float, float], ...],
    pocket_radius: float,
    ball_vel: list[float] | None = None,
    dt: float = 0.0,
) -> bool:
    """Verifica captura pela caçapa e aplica leve atração radial na borda da boca."""
    capture_limit_sq = (pocket_radius * POCKET_CAPTURE_RATIO) ** 2
    rim_limit_sq = (pocket_radius * POCKET_RIM_RATIO) ** 2

    for pocket in pockets:
        delta, dist_sq = displacement(ball_pos, pocket)
        if dist_sq <= capture_limit_sq:
            return True
        if ball_vel is not None and dt > 0.0 and dist_sq < rim_limit_sq and dist_sq > 1e-9:
            dist = sqrt(dist_sq)
            pull = POCKET_GRAVITY_PULL * dt
            ball_vel[0] += (delta[0] / dist) * pull
            ball_vel[1] += (delta[1] / dist) * pull

    return False


def resolve_cushion_bounce(
    pos: list[float],
    vel: list[float],
    radius: float,
    half_bounds: Sequence[float] = DEFAULT_TABLE_BOUNDS,
    restitution: float = DEFAULT_CUSHION_RESTITUTION,
    pockets: tuple[tuple[float, float], ...] | None = None,
    pocket_radius: float = DEFAULT_POCKET_RADIUS,
) -> bool:
    """Aplica o rebote elástico da bola nas 4 tabelas, respeitando a abertura das caçapas."""
    if pockets is not None and _is_near_pocket_mouth(
        pos, pockets, pocket_radius * POCKET_MOUTH_CLEARANCE
    ):
        outer_x = half_bounds[0] + pocket_radius * POCKET_OUTER_RATIO
        outer_y = half_bounds[1] + pocket_radius * POCKET_OUTER_RATIO
        bx = _bounce_1d(
            pos, vel, 0, (-outer_x, outer_x), restitution * POCKET_CUSHION_RESTITUTION_FACTOR
        )
        by = _bounce_1d(
            pos, vel, 1, (-outer_y, outer_y), restitution * POCKET_CUSHION_RESTITUTION_FACTOR
        )
        return bx or by

    bounced_x = _bounce_1d(
        pos, vel, 0, (-half_bounds[0] + radius, half_bounds[0] - radius), restitution
    )
    bounced_y = _bounce_1d(
        pos, vel, 1, (-half_bounds[1] + radius, half_bounds[1] - radius), restitution
    )
    return bounced_x or bounced_y


def compute_aim_raycast(
    cue_pos: Sequence[float],
    angle: float,
    balls: Sequence[dict[str, object]],
    radius: float,
    half_bounds: Sequence[float] = DEFAULT_TABLE_BOUNDS,
    max_length: float = RAYCAST_MAX_DISTANCE,
) -> dict[str, object]:
    """Calcula analiticamente o ponto de impacto da bola branca (Ghost Ball) contra bolas ou tabelas."""
    dx = cos(angle)
    dy = sin(angle)
    best_t = max_length
    hit_normal: tuple[float, float] | None = None

    min_x, max_x = -half_bounds[0] + radius, half_bounds[0] - radius
    min_y, max_y = -half_bounds[1] + radius, half_bounds[1] - radius

    if abs(dx) > 1e-8:
        tx = ((max_x if dx > 0.0 else min_x) - cue_pos[0]) / dx
        if 0.0 < tx < best_t:
            best_t = tx

    if abs(dy) > 1e-8:
        ty = ((max_y if dy > 0.0 else min_y) - cue_pos[1]) / dy
        if 0.0 < ty < best_t:
            best_t = ty

    two_r = 2.0 * radius
    two_r_sq = two_r * two_r

    for ball in balls:
        if ball.get("id") == 0 or ball.get("pocketed", False):
            continue
        b_pos = ball["pos"]
        if not isinstance(b_pos, list):
            continue
        ox = b_pos[0] - cue_pos[0]
        oy = b_pos[1] - cue_pos[1]
        proj = ox * dx + oy * dy
        if proj <= 0.0:
            continue
        perp_sq = (ox * ox + oy * oy) - (proj * proj)
        if perp_sq >= two_r_sq:
            continue
        t_hit = proj - sqrt(two_r_sq - perp_sq)
        if 0.0 < t_hit < best_t:
            best_t = t_hit
            gx = cue_pos[0] + dx * t_hit
            gy = cue_pos[1] + dy * t_hit
            nx = b_pos[0] - gx
            ny = b_pos[1] - gy
            norm_len = sqrt(nx * nx + ny * ny)
            if norm_len > 1e-8:
                hit_normal = (nx / norm_len, ny / norm_len)

    ghost_pos = (cue_pos[0] + dx * best_t, cue_pos[1] + dy * best_t)
    return {
        "distance": best_t,
        "ghost_pos": ghost_pos,
        "hit_normal": hit_normal,
    }


def main() -> None:
    """Executa a suíte de testes unitários do motor de física, anti-tunelamento e raycast."""
    import math

    assert dot_2d((1.0, 2.0), (3.0, 4.0)) == 11.0
    assert dot_2d((0.0, 0.0), (5.0, 5.0)) == 0.0

    p_a, v_a = [0.0, 0.0], [1.0, 0.0]
    p_b, v_b = [0.05, 0.0], [0.0, 0.0]
    collided = resolve_elastic_collision(p_a, v_a, p_b, v_b, radius=0.032)
    assert collided is True
    assert v_b[0] > 0.0
    assert v_a[0] < 1.0

    p_far_a, v_far_a = [0.0, 0.0], [1.0, 0.0]
    p_far_b, v_far_b = [0.5, 0.0], [0.0, 0.0]
    assert resolve_elastic_collision(p_far_a, v_far_a, p_far_b, v_far_b, radius=0.032) is False

    p_zero_a, v_zero_a = [0.0, 0.0], [0.0, 0.0]
    p_zero_b, v_zero_b = [0.0, 0.0], [0.0, 0.0]
    assert resolve_elastic_collision(p_zero_a, v_zero_a, p_zero_b, v_zero_b, radius=0.032) is False

    p_sep_a, v_sep_a = [0.0, 0.0], [-1.0, 0.0]
    p_sep_b, v_sep_b = [0.05, 0.0], [1.0, 0.0]
    assert resolve_elastic_collision(p_sep_a, v_sep_a, p_sep_b, v_sep_b, radius=0.032) is True
    assert v_sep_a[0] == -1.0

    p_in, v_in = [0.0, 0.0], [0.5, 0.5]
    assert resolve_cushion_bounce(p_in, v_in, radius=0.032, half_bounds=(0.90, 0.45)) is False

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

    pockets_test = ((0.88, 0.43), (-0.88, -0.43))
    assert check_pocket_fall([0.88, 0.43], pockets_test, 0.055) is True
    assert check_pocket_fall([0.0, 0.0], pockets_test, 0.055) is False

    test_balls = [
        {"id": 0, "pos": [-0.45, 0.0], "pocketed": False},
        {"id": 1, "pos": [0.0, 0.0], "pocketed": False},
    ]
    ray = compute_aim_raycast([-0.45, 0.0], 0.0, test_balls, radius=0.032)
    assert ray["hit_normal"] is not None
    ghost_x, ghost_y = ray["ghost_pos"]  # type: ignore[misc]
    assert math.isclose(ghost_x, -0.064, abs_tol=1e-4)
    assert math.isclose(ghost_y, 0.0, abs_tol=1e-4)

    print(
        "physics.py: elastic collision, cushion restitution, pocket jaws, and raycast tests passed successfully."
    )


if __name__ == "__main__":
    main()
