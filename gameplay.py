#!/usr/bin/env python3
"""
Lógica de jogo multiplayer (P1 vs P2), sistema de pontuação de sinuca, máquina de estados
e cinemática com sub-stepping do Sinucadas (Atividade 03).
Gerencia as 16 bolas, alternância de turnos, pontuação por bola e faltas (+4 pts ao oponente),
mira com raycast (Ghost Ball), tacada e estados (START, PLAYING, PAUSED, VICTORY, GAME_OVER).
"""

from math import ceil, cos, sin, sqrt
from typing import Any

import glfw

from graphics import (
    BALL_RADIUS,
    POCKET_POSITIONS,
    POCKET_RADIUS,
    TABLE_HEIGHT,
    TABLE_WIDTH,
)
from physics import (
    check_pocket_fall,
    compute_aim_raycast,
    dot_2d,
    resolve_cushion_bounce,
    resolve_elastic_collision,
)

MAX_LIVES = 3
TOTAL_OBJECT_BALLS = 15
FOUL_PENALTY_POINTS = 4

TABLE_BOUNDS: tuple[float, float] = (TABLE_WIDTH, TABLE_HEIGHT)
CUSHION_RESTITUTION: float = 0.85
BALL_RESTITUTION: float = 0.96
VELOCITY_STOP_EPSILON_SQ: float = 1e-4
ROLLING_FRICTION_BASE: float = 0.985
REFERENCE_FPS: float = 60.0

ROTATION_SPEED_NORMAL: float = 1.75
ROTATION_SPEED_PRECISION: float = 0.35
POWER_SPEED_NORMAL: float = 0.65
POWER_SPEED_PRECISION: float = 0.15
CUE_POWER_MIN: float = 0.0
CUE_POWER_MAX: float = 1.0

SHOT_FORCE_BASE: float = 0.35
SHOT_FORCE_SCALE: float = 2.35

SUBSTEP_SAFE_RATIO: float = 0.45
SUBSTEP_MIN: int = 4
SUBSTEP_MAX: int = 16

CUE_BALL_INITIAL_POS: tuple[float, float] = (-TABLE_WIDTH / 2.0, 0.0)
RACK_ORIGIN_X: float = TABLE_WIDTH / 3.0
RACK_DX_FACTOR: float = sqrt(3.0) / 2.0
RACK_DY_FACTOR: float = 1.02

STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_VICTORY = "VICTORY"
STATE_GAME_OVER = "GAME_OVER"

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
    """Inicializa o estado da mira, força da tacada e projeção da Ghost Ball."""
    return {
        "angle": 0.0,
        "power": 0.0,
        "visible": True,
        "aim_distance": 0.50,
        "ghost_pos": (0.0, 0.0),
        "hit_normal": None,
    }


def init_game_state() -> dict[str, Any]:
    """Inicializa a máquina de estados da partida multiplayer, turnos, pontos, bolas e vidas."""
    return {
        "state": STATE_START,
        "current_player": 1,
        "scores": [0, 0],
        "balls_pocketed": [0, 0],
        "player_pocketed_colors": [[], []],
        "pocketed_colors": [],
        "lives": MAX_LIVES,
        "score": 0,
        "shots": 0,
        "shot_in_progress": False,
        "turn_pocketed": 0,
        "turn_foul": False,
        "winner": 0,
    }


def _update_cue_aim_raycast(cue: dict[str, Any], balls: list[dict[str, Any]]) -> None:
    """Atualiza o raycast analítico da mira a partir da posição atual da bola branca."""
    if not balls:
        return
    ray = compute_aim_raycast(balls[0]["pos"], cue.get("angle", 0.0), balls, BALL_RADIUS)
    cue["aim_distance"] = ray["distance"]
    cue["ghost_pos"] = ray["ghost_pos"]
    cue["hit_normal"] = ray["hit_normal"]


def _update_cue_angle(cue: dict[str, Any], window: Any, dt: float) -> bool:
    """Atualiza o ângulo da mira do taco com suporte a ajuste fino (Shift ou A/D)."""
    is_precision = (
        glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    )
    speed = ROTATION_SPEED_PRECISION if is_precision else ROTATION_SPEED_NORMAL
    changed = False

    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        cue["angle"] += speed * dt
        changed = True
    elif glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        cue["angle"] += ROTATION_SPEED_PRECISION * dt
        changed = True

    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        cue["angle"] -= speed * dt
        changed = True
    elif glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        cue["angle"] -= ROTATION_SPEED_PRECISION * dt
        changed = True

    return changed


def _update_cue_power(cue: dict[str, Any], window: Any, dt: float) -> bool:
    """Ajusta a força acumulada do taco com suporte a ajuste fino (Shift ou W/S)."""
    is_precision = (
        glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    )
    speed = POWER_SPEED_PRECISION if is_precision else POWER_SPEED_NORMAL
    changed = False

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        cue["power"] = min(CUE_POWER_MAX, cue["power"] + speed * dt)
        changed = True
    elif glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cue["power"] = min(CUE_POWER_MAX, cue["power"] + POWER_SPEED_PRECISION * dt)
        changed = True

    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        cue["power"] = max(CUE_POWER_MIN, cue["power"] - speed * dt)
        changed = True
    elif glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cue["power"] = max(CUE_POWER_MIN, cue["power"] - POWER_SPEED_PRECISION * dt)
        changed = True

    return changed


def process_cue_controls(
    cue: dict[str, Any],
    window: Any,
    dt: float,
    balls: list[dict[str, Any]] | None = None,
    game_state: dict[str, Any] | None = None,
) -> None:
    """Processa entradas contínuas de mira e dosagem de força do taco."""
    if game_state is not None and game_state["state"] not in (STATE_START, STATE_PLAYING):
        return

    if cue.get("visible", False):
        moved_angle = _update_cue_angle(cue, window, dt)
        moved_power = _update_cue_power(cue, window, dt)
        if (moved_angle or moved_power) and game_state is not None:
            if game_state["state"] == STATE_START:
                game_state["state"] = STATE_PLAYING
        if balls is not None:
            _update_cue_aim_raycast(cue, balls)


def shoot_cue_ball(
    cue: dict[str, Any],
    balls: list[dict[str, Any]],
    game_state: dict[str, Any] | None = None,
) -> bool:
    """Aplica o impulso da tacada na bola branca e inicia a contabilização do turno."""
    if game_state is not None:
        if game_state["state"] in (STATE_PAUSED, STATE_VICTORY, STATE_GAME_OVER):
            return False
        if game_state["state"] == STATE_START:
            game_state["state"] = STATE_PLAYING

    if not cue.get("visible", False):
        return False

    power = cue.get("power", 0.0)
    force = SHOT_FORCE_BASE + power * SHOT_FORCE_SCALE
    angle = cue.get("angle", 0.0)

    balls[0]["vel"] = [force * cos(angle), force * sin(angle)]

    cue["power"] = 0.0
    cue["visible"] = False
    if game_state is not None:
        game_state["shots"] = game_state.get("shots", 0) + 1
        game_state["shot_in_progress"] = True
        game_state["turn_pocketed"] = 0
        game_state["turn_foul"] = False
    return True


def _create_cue_ball() -> dict[str, Any]:
    """Cria a estrutura de estado da bola branca na marca de saída."""
    return {
        "id": 0,
        "points": 0,
        "pos": list(CUE_BALL_INITIAL_POS),
        "vel": [0.0, 0.0],
        "color": CUE_BALL_COLOR,
        "pocketed": False,
        "is_eight": False,
    }


def _create_triangle_balls() -> list[dict[str, Any]]:
    """Gera o triângulo padrão de 15 bolas no foot spot com a bola 8 no centro."""
    balls: list[dict[str, Any]] = []
    x0 = RACK_ORIGIN_X
    diameter = BALL_RADIUS * 2.0
    dx = diameter * RACK_DX_FACTOR
    dy = diameter * RACK_DY_FACTOR

    color_index = 0
    for col in range(5):
        col_x = x0 + col * dx
        start_y = -(col * dy) / 2.0
        for row in range(col + 1):
            col_y = start_y + row * dy
            is_eight = col == 2 and row == 1
            if is_eight:
                color = COLOR_BLACK
                ball_num = 8
            elif color_index == 7:
                color = COLOR_YELLOW
                ball_num = 1
                color_index += 1
            else:
                color = BALL_COLORS[color_index % len(BALL_COLORS)]
                ball_num = color_index + 1 if color_index > 0 else 2
                color_index += 1

            balls.append(
                {
                    "id": len(balls) + 1,
                    "points": ball_num,
                    "pos": [col_x, col_y],
                    "vel": [0.0, 0.0],
                    "color": color,
                    "pocketed": False,
                    "is_eight": is_eight,
                }
            )
    return balls


def init_gameplay() -> list[dict[str, Any]]:
    """Inicializa as 16 bolas na mesa (bola branca na saída e triângulo no foot spot)."""
    return [_create_cue_ball(), *_create_triangle_balls()]


def reset_match(
    balls: list[dict[str, Any]],
    cue: dict[str, Any],
    game_state: dict[str, Any],
) -> None:
    """Reinicia integralmente o estado da partida multiplayer, bolas, taco e placares."""
    balls.clear()
    balls.extend(init_gameplay())
    cue.clear()
    cue.update(init_cue())
    _update_cue_aim_raycast(cue, balls)
    game_state.clear()
    game_state.update(init_game_state())


def _find_free_spot(
    target_pos: list[float], balls: list[dict[str, Any]], exclude_id: int
) -> list[float]:
    """Encontra uma posição livre de sobreposição próxima ao ponto alvo para reposicionar uma bola."""
    candidate = [target_pos[0], target_pos[1]]
    min_dist_sq = (2.05 * BALL_RADIUS) ** 2
    for step in range(20):
        offset_x = step * BALL_RADIUS * 1.1
        test_pos = [candidate[0] + offset_x, candidate[1]]
        if test_pos[0] > 0.82:
            test_pos[0] = candidate[0] - offset_x
        collision = False
        for other in balls:
            if other["id"] == exclude_id or other.get("pocketed", False):
                continue
            dx = test_pos[0] - other["pos"][0]
            dy = test_pos[1] - other["pos"][1]
            if dx * dx + dy * dy < min_dist_sq:
                collision = True
                break
        if not collision:
            return test_pos
    return candidate


def _decide_winner(game_state: dict[str, Any]) -> int:
    """Determina o jogador vencedor com base na pontuação acumulada."""
    scores = game_state.get("scores", [0, 0])
    if scores[0] > scores[1]:
        return 1
    if scores[1] > scores[0]:
        return 2
    balls_cnt = game_state.get("balls_pocketed", [0, 0])
    if balls_cnt[0] >= balls_cnt[1]:
        return 1
    return 2


def _apply_foul_penalty(game_state: dict[str, Any], reason: str) -> None:
    """Registra falta no turno atual, concede +4 pontos ao adversário e desconta vida."""
    cur_idx = int(game_state.get("current_player", 1)) - 1
    opp_idx = 1 - cur_idx
    game_state["turn_foul"] = True
    game_state["scores"][opp_idx] += FOUL_PENALTY_POINTS
    game_state["lives"] = max(0, game_state["lives"] - 1)
    print(
        f"[Sinucadas] ⚠️ Falta do Jogador {cur_idx + 1} ({reason})! "
        f"+{FOUL_PENALTY_POINTS} pts para o Jogador {opp_idx + 1}."
    )
    if game_state["lives"] == 0:
        game_state["state"] = STATE_GAME_OVER
        game_state["winner"] = opp_idx + 1
        print(
            f"[Sinucadas] 💀 Fim de Jogo por limite de faltas! Vitória do Jogador {opp_idx + 1}!"
        )


def _handle_pocket_event(
    ball: dict[str, Any],
    all_balls: list[dict[str, Any]] | None = None,
    game_state: dict[str, Any] | None = None,
) -> bool:
    """Aplica regras de pontuação por jogador, faltas na branca/bola 8 e encaçapamento."""
    if ball["id"] == 0:
        ball["pos"] = (
            _find_free_spot(list(CUE_BALL_INITIAL_POS), all_balls, 0)
            if all_balls
            else list(CUE_BALL_INITIAL_POS)
        )
        ball["vel"] = [0.0, 0.0]
        if game_state is not None:
            _apply_foul_penalty(game_state, "bola branca na caçapa")
        return False

    if ball.get("is_eight", False) and all_balls is not None and game_state is not None:
        remaining_regular = sum(
            1
            for b in all_balls
            if b["id"] != 0 and not b.get("is_eight", False) and not b.get("pocketed", False)
        )
        if remaining_regular > 0:
            ball["vel"] = [0.0, 0.0]
            _apply_foul_penalty(game_state, "Bola 8 encaçapada prematuramente")
            if game_state["state"] == STATE_GAME_OVER:
                ball["pocketed"] = True
                ball["pos"] = [-2.0, -2.0]
                return True
            ball["pos"] = _find_free_spot([0.30, 0.0], all_balls, ball["id"])
            return False

    ball["pocketed"] = True
    ball["vel"] = [0.0, 0.0]
    ball["pos"] = [-2.0, -2.0]
    pts = int(ball.get("points", ball["id"]))

    if game_state is not None:
        cur_player = int(game_state.get("current_player", 1))
        p_idx = cur_player - 1
        game_state["scores"][p_idx] += pts
        game_state["balls_pocketed"][p_idx] += 1
        game_state["player_pocketed_colors"][p_idx].append(ball["color"])
        game_state["turn_pocketed"] = game_state.get("turn_pocketed", 0) + 1
        game_state["score"] = game_state.get("score", 0) + 1
        game_state.setdefault("pocketed_colors", []).append(ball["color"])

        print(
            f"[Sinucadas] 🎯 Jogador {cur_player} encaçapou a Bola {ball['id']} (+{pts} pts)! "
            f"Placar: P1 {game_state['scores'][0]} pts x P2 {game_state['scores'][1]} pts"
        )

        if game_state["score"] >= TOTAL_OBJECT_BALLS:
            game_state["state"] = STATE_VICTORY
            game_state["winner"] = _decide_winner(game_state)
            print(
                f"[Sinucadas] 🏆 Fim de Partida! Jogador {game_state['winner']} venceu "
                f"({game_state['scores'][0]} x {game_state['scores'][1]} pts)!"
            )
    else:
        print(f"[Sinucadas] 🎯 Bola {ball['id']} encaçapada!")

    return True


def _compute_substeps(balls: list[dict[str, Any]], dt: float) -> int:
    """Determina o número de sub-passos temporais para impedir tunelamento em altas velocidades."""
    max_speed_sq = max(
        (dot_2d(b["vel"], b["vel"]) for b in balls if not b.get("pocketed", False)),
        default=0.0,
    )
    if max_speed_sq <= 0.0 or dt <= 0.0:
        return 1
    max_disp = sqrt(max_speed_sq) * dt
    safe_step = BALL_RADIUS * SUBSTEP_SAFE_RATIO
    return max(SUBSTEP_MIN, min(SUBSTEP_MAX, int(ceil(max_disp / safe_step))))


def _step_ball_kinematics(
    balls: list[dict[str, Any]],
    pockets: tuple[tuple[float, float], ...],
    pocket_radius: float,
    sub_dt: float,
    game_state: dict[str, Any] | None = None,
) -> None:
    """Avança posições em um sub-passo temporal, verifica caçapas e aplica reflexão nas tabelas."""
    for ball in balls:
        if ball.get("pocketed", False):
            continue

        ball["pos"][0] += ball["vel"][0] * sub_dt
        ball["pos"][1] += ball["vel"][1] * sub_dt

        if check_pocket_fall(ball["pos"], pockets, pocket_radius, ball["vel"], sub_dt):
            if _handle_pocket_event(ball, balls, game_state):
                continue

        resolve_cushion_bounce(
            ball["pos"],
            ball["vel"],
            BALL_RADIUS,
            TABLE_BOUNDS,
            restitution=CUSHION_RESTITUTION,
            pockets=pockets,
            pocket_radius=pocket_radius,
        )


def _resolve_all_ball_collisions(active_balls: list[dict[str, Any]], passes: int = 2) -> None:
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
                    restitution=BALL_RESTITUTION,
                )


def _apply_friction_and_drag(active_balls: list[dict[str, Any]], friction: float) -> None:
    """Aplica o atrito de rolagem do feltro e repousa bolas com velocidade residual."""
    for ball in active_balls:
        ball["vel"][0] *= friction
        ball["vel"][1] *= friction

        if dot_2d(ball["vel"], ball["vel"]) < VELOCITY_STOP_EPSILON_SQ:
            ball["vel"] = [0.0, 0.0]


def _finalize_turn_if_needed(game_state: dict[str, Any]) -> None:
    """Avalia o resultado da tacada ao parar as bolas: mantém turno se pontuou sem falta, ou alterna jogador."""
    if not game_state.get("shot_in_progress", False):
        return
    game_state["shot_in_progress"] = False
    if game_state["state"] in (STATE_VICTORY, STATE_GAME_OVER):
        return

    cur_player = int(game_state.get("current_player", 1))
    if game_state.get("turn_foul", False) or int(game_state.get("turn_pocketed", 0)) == 0:
        next_player = 2 if cur_player == 1 else 1
        game_state["current_player"] = next_player
        print(f"[Sinucadas] 🔄 Passagem de turno: agora é a vez do Jogador {next_player}!")
    else:
        print(
            f"[Sinucadas] 🔥 Jogador {cur_player} encaçapou {game_state['turn_pocketed']} bola(s) e continua na vez!"
        )
    game_state["turn_pocketed"] = 0
    game_state["turn_foul"] = False


def _check_cue_readiness(
    active_balls: list[dict[str, Any]],
    cue: dict[str, Any] | None,
    all_balls: list[dict[str, Any]] | None = None,
    game_state: dict[str, Any] | None = None,
) -> None:
    """Restaura a visibilidade do taco, resolve a troca de turno e atualiza o raycast quando as bolas param."""
    if game_state is not None and game_state["state"] in (STATE_VICTORY, STATE_GAME_OVER):
        if cue is not None:
            cue["visible"] = False
        return

    if cue and not cue.get("visible", False):
        all_stopped = all(dot_2d(b["vel"], b["vel"]) == 0.0 for b in active_balls)
        if all_stopped:
            if game_state is not None:
                _finalize_turn_if_needed(game_state)
            cue["visible"] = True
            if all_balls is not None:
                _update_cue_aim_raycast(cue, all_balls)


def update_gameplay(
    balls: list[dict[str, Any]],
    cue: dict[str, Any] | None,
    dt: float,
    pockets: tuple[tuple[float, float], ...] = POCKET_POSITIONS,
    pocket_radius: float = POCKET_RADIUS,
    game_state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Atualiza a física com sub-stepping anti-tunelamento, caçapas, tabelas, colisões e turnos."""
    if game_state is not None and game_state["state"] == STATE_PAUSED:
        return balls

    substeps = _compute_substeps(balls, dt)
    sub_dt = dt / substeps
    friction = ROLLING_FRICTION_BASE ** (dt * REFERENCE_FPS)

    for _ in range(substeps):
        _step_ball_kinematics(balls, pockets, pocket_radius, sub_dt, game_state)
        active_balls = [b for b in balls if not b.get("pocketed", False)]
        _resolve_all_ball_collisions(active_balls, passes=2)

    active_balls = [b for b in balls if not b.get("pocketed", False)]
    _apply_friction_and_drag(active_balls, friction)
    _check_cue_readiness(active_balls, cue, balls, game_state)

    if cue and cue.get("visible", False):
        _update_cue_aim_raycast(cue, balls)

    return balls


def main() -> None:
    """Executa a suíte de testes unitários da mecânica multiplayer, turnos, pontuação e física."""
    import math
    from unittest.mock import MagicMock

    balls = init_gameplay()
    cue = init_cue()
    state = init_game_state()
    assert len(balls) == 16
    assert balls[0]["id"] == 0
    assert state["current_player"] == 1
    assert state["scores"] == [0, 0]

    cue["power"] = 0.5
    cue["angle"] = 0.0
    shot_success = shoot_cue_ball(cue, balls, state)
    assert shot_success is True
    assert state["state"] == STATE_PLAYING
    assert state["shot_in_progress"] is True
    assert cue["visible"] is False
    assert balls[0]["vel"][0] > 0.0
    assert math.isclose(balls[0]["vel"][1], 0.0)

    balls[0]["vel"] = [0.0, 0.0]
    _check_cue_readiness(balls, cue, balls, state)
    assert cue["visible"] is True
    assert state["current_player"] == 2

    shoot_cue_ball(cue, balls, state)
    numbered_ball = balls[1]
    pocketed_handled = _handle_pocket_event(numbered_ball, balls, state)
    assert pocketed_handled is True
    assert state["scores"][1] > 0
    assert state["balls_pocketed"][1] == 1
    balls[0]["vel"] = [0.0, 0.0]
    _check_cue_readiness([b for b in balls if not b["pocketed"]], cue, balls, state)
    assert state["current_player"] == 2

    shoot_cue_ball(cue, balls, state)
    foul_handled = _handle_pocket_event(balls[0], balls, state)
    assert foul_handled is False
    assert state["scores"][0] == FOUL_PENALTY_POINTS
    balls[0]["vel"] = [0.0, 0.0]
    _check_cue_readiness([b for b in balls if not b["pocketed"]], cue, balls, state)
    assert state["current_player"] == 1

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
        test_cue_ctrl = init_cue()
        process_cue_controls(test_cue_ctrl, mock_win, dt=0.1, balls=balls)
        assert test_cue_ctrl["angle"] > 0.0
        assert test_cue_ctrl["power"] > 0.0
    finally:
        glfw.get_key = orig_get_key

    reset_match(balls, cue, state)
    assert state["scores"] == [0, 0] and state["current_player"] == 1

    print(
        f"gameplay.py: multiplayer turns, pool scoring (+foul points), and {len(balls)} balls verified successfully."
    )


if __name__ == "__main__":
    main()
