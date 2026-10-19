#!/usr/bin/env python3
"""
Lógica de jogo e estado das bolas para o Sinucadas.
Gerencia a criação e posicionamento inicial das 16 bolas de sinuca (bola branca e triângulo de 15 bolas).
"""

from math import cos, sin
from typing import Any

import glfw

from graphics import POCKET_POSITIONS, POCKET_RADIUS
from physics import (
    _dot_2d,
    check_pocket_fall,
    resolve_cushion_bounce,
    resolve_elastic_collision,
)

BALL_RADIUS = 0.032

COLOR_YELLOW = (0.95, 0.85, 0.15, 1.0)
COLOR_BLUE = (0.15, 0.40, 0.85, 1.0)
COLOR_RED = (0.85, 0.15, 0.15, 1.0)
COLOR_PURPLE = (0.55, 0.15, 0.75, 1.0)
COLOR_ORANGE = (0.95, 0.50, 0.10, 1.0)
COLOR_GREEN = (0.15, 0.65, 0.25, 1.0)
COLOR_BROWN = (0.55, 0.20, 0.15, 1.0)
COLOR_BLACK = (0.10, 0.10, 0.10, 1.0)
COLOR_STRIPED_YELLOW = (0.90, 0.75, 0.20, 1.0)
COLOR_STRIPED_BLUE = (0.25, 0.65, 0.90, 1.0)
COLOR_STRIPED_RED = (0.90, 0.30, 0.30, 1.0)
COLOR_STRIPED_PURPLE = (0.70, 0.35, 0.85, 1.0)
COLOR_STRIPED_ORANGE = (0.95, 0.65, 0.25, 1.0)
COLOR_STRIPED_GREEN = (0.35, 0.80, 0.45, 1.0)
COLOR_STRIPED_BROWN = (0.60, 0.10, 0.30, 1.0)

BALL_COLORS = (
    COLOR_YELLOW,
    COLOR_BLUE,
    COLOR_RED,
    COLOR_PURPLE,
    COLOR_ORANGE,
    COLOR_GREEN,
    COLOR_BROWN,
    COLOR_BLACK,
    COLOR_STRIPED_YELLOW,
    COLOR_STRIPED_BLUE,
    COLOR_STRIPED_RED,
    COLOR_STRIPED_PURPLE,
    COLOR_STRIPED_ORANGE,
    COLOR_STRIPED_GREEN,
    COLOR_STRIPED_BROWN,
)

CUE_BALL_COLOR = (0.96, 0.96, 0.96, 1.0)


def init_cue() -> dict[str, Any]:
    """Inicializa o estado da mira e da força acumulada do taco de sinuca."""
    return {"angle": 0.0, "power": 0.0, "visible": True}


def _update_cue_angle(cue: dict[str, Any], window: Any, dt: float) -> None:
    """Atualiza o ângulo da mira do taco com suporte a ajuste fino (Shift ou A/D)."""
    is_precision = (
        glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    )
    speed = 0.35 if is_precision else 1.75

    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        cue["angle"] += speed * dt
    elif glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        cue["angle"] += 0.35 * dt

    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        cue["angle"] -= speed * dt
    elif glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        cue["angle"] -= 0.35 * dt


def _update_cue_power(cue: dict[str, Any], window: Any, dt: float) -> None:
    """Ajusta a força acumulada do taco com suporte a ajuste fino (Shift ou W/S)."""
    is_precision = (
        glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    )
    speed = 0.15 if is_precision else 0.65

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        cue["power"] = min(1.0, cue["power"] + speed * dt)
    elif glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cue["power"] = min(1.0, cue["power"] + 0.15 * dt)

    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        cue["power"] = max(0.0, cue["power"] - speed * dt)
    elif glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cue["power"] = max(0.0, cue["power"] - 0.15 * dt)


def process_cue_controls(cue: dict[str, Any], window: Any, dt: float) -> None:
    """Processa entradas contínuas de mira e dosagem de força do taco."""
    if cue.get("visible", False):
        _update_cue_angle(cue, window, dt)
        _update_cue_power(cue, window, dt)


def shoot_cue_ball(cue: dict[str, Any], balls: list[dict[str, Any]]) -> bool:
    """Aplica o impulso da tacada na bola branca com base no ângulo e na força acumulada."""
    if not cue.get("visible", False):
        return False

    power = cue.get("power", 0.0)
    force = 0.25 + power * 2.25
    angle = cue.get("angle", 0.0)

    balls[0]["vel"] = [force * cos(angle), force * sin(angle)]

    cue["power"] = 0.0
    cue["visible"] = False
    return True


def _create_cue_ball() -> dict[str, Any]:
    """Cria a estrutura de estado da bola branca na marca de saída."""
    return {
        "id": 0,
        "pos": [-0.45, 0.0],
        "vel": [0.0, 0.0],
        "color": CUE_BALL_COLOR,
        "pocketed": False,
    }


def _create_triangle_balls() -> list[dict[str, Any]]:
    """Gera o triângulo padrão de 15 bolas no foot spot com a bola 8 no centro."""
    balls: list[dict[str, Any]] = []
    x0 = 0.30
    diameter = BALL_RADIUS * 2.0
    dx = diameter * 0.866
    dy = diameter * 1.02

    color_index = 0
    for col in range(5):
        col_x = x0 + col * dx
        start_y = -(col * dy) / 2.0
        for row in range(col + 1):
            col_y = start_y + row * dy
            if col == 2 and row == 1:
                color = COLOR_BLACK
            elif color_index == 7:
                color = COLOR_YELLOW
                color_index += 1
            else:
                color = BALL_COLORS[color_index % len(BALL_COLORS)]
                color_index += 1

            balls.append(
                {
                    "id": len(balls) + 1,
                    "pos": [col_x, col_y],
                    "vel": [0.0, 0.0],
                    "color": color,
                    "pocketed": False,
                }
            )
    return balls


def init_gameplay() -> list[dict[str, Any]]:
    """Inicializa as 16 bolas na mesa (bola branca na saída e triângulo no foot spot)."""
    return [_create_cue_ball(), *_create_triangle_balls()]


def _handle_pocket_event(ball: dict[str, Any]) -> bool:
    """Aplica penalidade de falta na bola branca ou encaçapa bola numerada. Retorna True se removida."""
    if ball["id"] == 0:
        print("[Sinucadas] ⚠️ Foul! Cue ball pocketed — repositioned at head spot.")
        ball["pos"] = [-0.45, 0.0]
        ball["vel"] = [0.0, 0.0]
        return False

    print(f"[Sinucadas] 🎯 Ball {ball['id']} pocketed successfully!")
    ball["pocketed"] = True
    ball["vel"] = [0.0, 0.0]
    ball["pos"] = [-2.0, -2.0]
    return True


def _update_ball_kinematics(
    balls: list[dict[str, Any]],
    pockets: tuple[tuple[float, float], ...],
    pocket_radius: float,
    dt: float,
) -> None:
    """Avança posições das bolas, verifica encaçapamento e aplica reflexão nas tabelas."""
    for ball in balls:
        if ball.get("pocketed", False):
            continue

        ball["pos"][0] += ball["vel"][0] * dt
        ball["pos"][1] += ball["vel"][1] * dt

        if check_pocket_fall(ball["pos"], pockets, pocket_radius) and _handle_pocket_event(
            ball
        ):
            continue

        resolve_cushion_bounce(
            ball["pos"], ball["vel"], BALL_RADIUS, (0.90, 0.45), restitution=0.85
        )


def _resolve_all_ball_collisions(active_balls: list[dict[str, Any]], passes: int = 3) -> None:
    """Resolve sobreposições e trocas de momento elástico entre pares de bolas ativas."""
    num_active = len(active_balls)
    for _ in range(passes):
        for i in range(num_active):
            for j in range(i + 1, num_active):
                resolve_elastic_collision(
                    active_balls[i]["pos"],
                    active_balls[i]["vel"],
                    active_balls[j]["pos"],
                    active_balls[j]["vel"],
                    BALL_RADIUS,
                    restitution=0.96,
                )


def _apply_friction_and_drag(active_balls: list[dict[str, Any]], friction: float) -> None:
    """Aplica o atrito de rolagem do feltro e repousa bolas com velocidade residual."""
    for ball in active_balls:
        ball["vel"][0] *= friction
        ball["vel"][1] *= friction

        if _dot_2d(ball["vel"], ball["vel"]) < 0.0001:
            ball["vel"] = [0.0, 0.0]


def _check_cue_readiness(
    active_balls: list[dict[str, Any]], cue: dict[str, Any] | None
) -> None:
    """Restaura a visibilidade do taco quando todas as bolas atingem repouso completo."""
    if cue and not cue.get("visible", False):
        all_stopped = all(_dot_2d(b["vel"], b["vel"]) == 0.0 for b in active_balls)
        if all_stopped:
            cue["visible"] = True


def update_gameplay(
    balls: list[dict[str, Any]],
    cue: dict[str, Any] | None,
    dt: float,
    pockets: tuple[tuple[float, float], ...] = POCKET_POSITIONS,
    pocket_radius: float = POCKET_RADIUS,
) -> list[dict[str, Any]]:
    """Atualiza física das bolas: movimentação, caçapas, tabelas, colisões mútuas e atrito."""
    friction = 0.985 ** (dt * 60.0)

    _update_ball_kinematics(balls, pockets, pocket_radius, dt)
    active_balls = [b for b in balls if not b.get("pocketed", False)]
    _resolve_all_ball_collisions(active_balls)
    _apply_friction_and_drag(active_balls, friction)
    _check_cue_readiness(active_balls, cue)

    return balls


if __name__ == "__main__":
    def _test_gameplay_module() -> None:
        import math
        from unittest.mock import MagicMock

        # 1. Initialize gameplay and verify balls hierarchy
        balls = init_gameplay()
        cue = init_cue()
        assert len(balls) == 16, f"Expected 16 balls, got {len(balls)}"
        assert balls[0]["id"] == 0, "Ball 0 must be cue ball"
        assert balls[0]["pos"] == [-0.45, 0.0]
        assert balls[0]["pocketed"] is False
        assert cue["visible"] is True, "Cue must start visible"
        assert cue["power"] == 0.0 and cue["angle"] == 0.0

        # Check 8-ball (black ball at center of triangle)
        black_balls = [b for b in balls[1:] if b["color"] == COLOR_BLACK]
        assert len(black_balls) == 1, "Must contain exactly one black 8-ball"

        # 2. Cue shooting dynamics
        cue["power"] = 0.5
        cue["angle"] = 0.0
        shot_success = shoot_cue_ball(cue, balls)
        assert shot_success is True
        assert cue["visible"] is False
        assert cue["power"] == 0.0
        assert balls[0]["vel"][0] > 0.0
        assert math.isclose(balls[0]["vel"][1], 0.0)

        # Cannot shoot again while cue is invisible
        assert shoot_cue_ball(cue, balls) is False

        # 3. Pocket event: foul on cue ball vs numbered ball pocketed
        foul_handled = _handle_pocket_event(balls[0])
        assert foul_handled is False, "Foul should not remove cue ball"
        assert balls[0]["pos"] == [-0.45, 0.0]
        assert balls[0]["vel"] == [0.0, 0.0]
        assert balls[0]["pocketed"] is False

        numbered_ball = balls[1]
        pocketed_handled = _handle_pocket_event(numbered_ball)
        assert pocketed_handled is True, "Numbered ball should be pocketed"
        assert numbered_ball["pocketed"] is True
        assert numbered_ball["pos"] == [-2.0, -2.0]

        # 4. Cue readiness checking
        cue_test = {"visible": False}
        balls[2]["vel"] = [0.1, 0.0]
        _check_cue_readiness(balls, cue_test)
        assert cue_test["visible"] is False, "Cue must remain hidden while balls are in motion"

        balls[2]["vel"] = [0.0, 0.0]
        _check_cue_readiness(balls, cue_test)
        assert cue_test["visible"] is True, "Cue must appear once all balls stop"

        # 5. Cue controls with mocked GLFW window
        mock_win = MagicMock()
        mock_win_key = {
            glfw.KEY_LEFT_SHIFT: glfw.RELEASE,
            glfw.KEY_RIGHT_SHIFT: glfw.RELEASE,
            glfw.KEY_LEFT: glfw.PRESS,
            glfw.KEY_A: glfw.RELEASE,
            glfw.KEY_RIGHT: glfw.RELEASE,
            glfw.KEY_D: glfw.RELEASE,
            glfw.KEY_UP: glfw.PRESS,
            glfw.KEY_W: glfw.RELEASE,
            glfw.KEY_DOWN: glfw.RELEASE,
            glfw.KEY_S: glfw.RELEASE,
        }
        orig_get_key = glfw.get_key
        try:
            glfw.get_key = MagicMock(side_effect=lambda w, k: mock_win_key.get(k, glfw.RELEASE))
            test_cue_ctrl = {"angle": 0.0, "power": 0.0, "visible": True}
            process_cue_controls(test_cue_ctrl, mock_win, dt=0.1)
            assert test_cue_ctrl["angle"] > 0.0
            assert test_cue_ctrl["power"] > 0.0
        finally:
            glfw.get_key = orig_get_key

        # 6. Gameplay integration step
        balls = init_gameplay()
        cue = init_cue()
        balls[0]["vel"] = [1.0, 0.0]
        balls = update_gameplay(balls, cue, dt=0.016)
        assert balls[0]["pos"][0] != -0.45

        print(f"gameplay.py: {len(balls)} balls, rack formation, fouls, and kinematics verified successfully.")

    _test_gameplay_module()
