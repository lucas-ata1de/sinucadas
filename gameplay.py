#!/usr/bin/env python3
"""
Lógica de jogo e estado das bolas para o Sinucadas.
Gerencia a criação e posicionamento inicial das 16 bolas de sinuca (bola branca e triângulo de 15 bolas).
"""

from math import cos, sin
from typing import Any

import glfw

from graphics import POSICOES_CACAPAS, RAIO_CACAPA
from physics import (
    check_pocket_fall,
    resolve_cushion_bounce,
    resolve_elastic_collision,
)

RAIO_BOLA = 0.032

CORES_BOLAS = (
    (0.95, 0.85, 0.15, 1.0),
    (0.15, 0.40, 0.85, 1.0),
    (0.85, 0.15, 0.15, 1.0),
    (0.55, 0.15, 0.75, 1.0),
    (0.95, 0.50, 0.10, 1.0),
    (0.15, 0.65, 0.25, 1.0),
    (0.55, 0.20, 0.15, 1.0),
    (0.10, 0.10, 0.10, 1.0),
    (0.90, 0.75, 0.20, 1.0),
    (0.25, 0.65, 0.90, 1.0),
    (0.90, 0.30, 0.30, 1.0),
    (0.70, 0.35, 0.85, 1.0),
    (0.95, 0.65, 0.25, 1.0),
    (0.35, 0.80, 0.45, 1.0),
    (0.60, 0.10, 0.30, 1.0),
)

COR_BOLA_BRANCA = (0.96, 0.96, 0.96, 1.0)


def init_cue() -> dict[str, Any]:
    """Inicializa o estado da mira e da força acumulada do taco de sinuca."""
    return {
        "angle": 0.0,
        "power": 0.0,
        "visible": True,
    }


def process_cue_controls(cue: dict[str, Any], window: Any, dt: float) -> None:
    """Processa entradas contínuas de mira (Shift para precisão) e dosagem de força do taco."""
    if not cue.get("visible", False):
        return

    is_precision = (
        glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    )

    rotation_speed = 0.35 if is_precision else 1.75
    power_speed = 0.65

    if (
        glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_A) == glfw.PRESS
    ):
        cue["angle"] += (0.35 if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS else rotation_speed) * dt
    if (
        glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_D) == glfw.PRESS
    ):
        cue["angle"] -= (0.35 if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS else rotation_speed) * dt

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        cue["power"] = min(1.0, cue["power"] + power_speed * dt)
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        cue["power"] = max(0.0, cue["power"] - power_speed * dt)


def shoot_cue_ball(cue: dict[str, Any], balls: list[dict[str, Any]]) -> bool:
    """Aplica o impulso da tacada na bola branca com base no ângulo e na força acumulada."""
    if not cue.get("visible", False):
        return False

    power = cue.get("power", 0.0)
    force = 0.25 + power * 2.25
    angle = cue.get("angle", 0.0)

    balls[0]["vel"][0] = force * cos(angle)
    balls[0]["vel"][1] = force * sin(angle)

    cue["power"] = 0.0
    cue["visible"] = False
    return True


def init_gameplay() -> list[dict[str, Any]]:
    """Inicializa as 16 bolas na mesa (bola branca na saída e triângulo no foot spot)."""
    balls: list[dict[str, Any]] = []

    balls.append(
        {
            "id": 0,
            "pos": [-0.45, 0.0],
            "vel": [0.0, 0.0],
            "color": COR_BOLA_BRANCA,
            "pocketed": False,
        }
    )

    x0 = 0.30
    diametro = RAIO_BOLA * 2.0
    dx = diametro * 0.866
    dy = diametro * 1.02

    idx_cor = 0
    for col in range(5):
        col_x = x0 + col * dx
        start_y = -(col * dy) / 2.0
        for row in range(col + 1):
            col_y = start_y + row * dy
            if col == 2 and row == 1:
                cor = CORES_BOLAS[7]
            elif idx_cor == 7:
                cor = CORES_BOLAS[0]
                idx_cor += 1
            else:
                cor = CORES_BOLAS[idx_cor % len(CORES_BOLAS)]
                idx_cor += 1

            balls.append(
                {
                    "id": len(balls),
                    "pos": [col_x, col_y],
                    "vel": [0.0, 0.0],
                    "color": cor,
                    "pocketed": False,
                }
            )

    return balls


def update_gameplay(
    balls: list[dict[str, Any]],
    cue: dict[str, Any] | None,
    dt: float,
    pockets: tuple[tuple[float, float], ...] = POSICOES_CACAPAS,
    pocket_radius: float = RAIO_CACAPA,
) -> list[dict[str, Any]]:
    """Atualiza física das bolas: movimentação, caçapas, tabelas, colisões mútuas e atrito."""
    friction = 0.985 ** (dt * 60.0)

    for ball in balls:
        if ball.get("pocketed", False):
            continue

        ball["pos"][0] += ball["vel"][0] * dt
        ball["pos"][1] += ball["vel"][1] * dt

        if check_pocket_fall(ball["pos"], pockets, pocket_radius):
            if ball["id"] == 0:
                print(
                    "[Sinucadas] ⚠️ Falta! Bola branca encaçapada — reposicionada na marca de saída."
                )
                ball["pos"] = [-0.45, 0.0]
                ball["vel"] = [0.0, 0.0]
            else:
                print(f"[Sinucadas] 🎯 Bola {ball['id']} encaçapada com sucesso!")
                ball["pocketed"] = True
                ball["vel"] = [0.0, 0.0]
                ball["pos"] = [-2.0, -2.0]
                continue

        resolve_cushion_bounce(
            ball["pos"], ball["vel"], RAIO_BOLA, 0.90, 0.45, restitution=0.85
        )

    active_balls = [b for b in balls if not b.get("pocketed", False)]
    num_active = len(active_balls)
    for _ in range(3):
        for i in range(num_active):
            for j in range(i + 1, num_active):
                resolve_elastic_collision(
                    active_balls[i]["pos"],
                    active_balls[i]["vel"],
                    active_balls[j]["pos"],
                    active_balls[j]["vel"],
                    RAIO_BOLA,
                    restitution=0.96,
                )

    for ball in active_balls:
        ball["vel"][0] *= friction
        ball["vel"][1] *= friction

        if (ball["vel"][0] ** 2 + ball["vel"][1] ** 2) < 0.0001:
            ball["vel"][0] = 0.0
            ball["vel"][1] = 0.0

    if cue and not cue.get("visible", False):
        all_stopped = all(
            b["vel"][0] == 0.0 and b["vel"][1] == 0.0 for b in active_balls
        )
        if all_stopped:
            cue["visible"] = True

    return balls


if __name__ == "__main__":
    b = init_gameplay()
    c = init_cue()
    assert len(b) == 16, f"Esperado 16 bolas, obtido {len(b)}"
    assert c["visible"] is True, "Taco deve iniciar visível"
    print(f"gameplay.py: {len(b)} bolas e taco inicializados com sucesso na mesa.")
