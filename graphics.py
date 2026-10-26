#!/usr/bin/env python3
"""
Módulo de renderização, HUD geométrico multiplayer e primitivas gráficas do Sinucadas (Atividade 03).
Gerencia a compilação dos shaders (OpenGL 4.0 Core), geometria da mesa, caçapas, bolas,
taco com cores distintas por jogador (P1 Azul Safira vs P2 Vermelho Rubi), mira com Ghost Ball,
animações autônomas baseadas no tempo e placar multiplayer em geometria.
Todos os VBOs são alocados estaticamente uma única vez na inicialização.
"""

import sys
from math import atan2, cos, pi, sin
from pathlib import Path
from typing import Any, cast

import glfw
import moderngl
import numpy as np


def _resolve_shader_code(source: str | Path | None) -> str | None:
    """Lê o código-fonte de um shader a partir de arquivo ou preserva a string GLSL direta."""
    if source is None:
        return None
    if isinstance(source, Path) or (
        isinstance(source, str) and "\n" not in source and Path(source).is_file()
    ):
        return Path(source).read_text(encoding="utf-8")
    return str(source)


def create_program(
    ctx: moderngl.Context,
    vertex_shader: str | Path,
    fragment_shader: str | Path | None = None,
    geometry_shader: str | Path | None = None,
    tess_control_shader: str | Path | None = None,
    tess_evaluation_shader: str | Path | None = None,
) -> moderngl.Program:
    """Compila e vincula um programa ModernGL a partir de arquivos (Path) ou strings de código GLSL."""
    vs = _resolve_shader_code(vertex_shader)
    fs = _resolve_shader_code(fragment_shader)
    gs = _resolve_shader_code(geometry_shader)
    tcs = _resolve_shader_code(tess_control_shader)
    tes = _resolve_shader_code(tess_evaluation_shader)

    try:
        kwargs: dict[str, Any] = {"vertex_shader": vs}
        if fs is not None:
            kwargs["fragment_shader"] = fs
        if gs is not None:
            kwargs["geometry_shader"] = gs
        if tcs is not None:
            kwargs["tess_control_shader"] = tcs
        if tes is not None:
            kwargs["tess_evaluation_shader"] = tes
        return ctx.program(**kwargs)
    except moderngl.Error as err:
        print(f"\n[SHADER COMPILATION ERROR]\n{err}\n", file=sys.stderr)
        raise


def _set_uniform(prog: moderngl.Program, name: str, value: Any) -> None:
    """Atualiza o valor de um uniforme no programa GLSL com tipagem estática segura."""
    cast(moderngl.Uniform, prog[name]).value = value


SHADERS_DIR = Path(__file__).parent / "shaders"

TABLE_WIDTH = 0.90
TABLE_HEIGHT = 0.45
CUSHION_THICKNESS = 0.10

POCKET_BOTTOM_LEFT = (-0.88, -0.43)
POCKET_BOTTOM_CENTER = (0.00, -0.45)
POCKET_BOTTOM_RIGHT = (0.88, -0.43)
POCKET_TOP_LEFT = (-0.88, 0.43)
POCKET_TOP_CENTER = (0.00, 0.45)
POCKET_TOP_RIGHT = (0.88, 0.43)

POCKET_POSITIONS = (
    POCKET_BOTTOM_LEFT,
    POCKET_BOTTOM_CENTER,
    POCKET_BOTTOM_RIGHT,
    POCKET_TOP_LEFT,
    POCKET_TOP_CENTER,
    POCKET_TOP_RIGHT,
)

POCKET_RADIUS = 0.055
BALL_RADIUS = 0.032

FELT_GREEN = (0.10, 0.52, 0.24, 1.0)
FELT_BLUE = (0.12, 0.38, 0.65, 1.0)
FELT_RED = (0.55, 0.12, 0.18, 1.0)
FELT_BLACK = (0.16, 0.18, 0.20, 1.0)

FELT_COLORS = (FELT_GREEN, FELT_BLUE, FELT_RED, FELT_BLACK)

WOOD_COLOR = (0.35, 0.18, 0.08, 1.0)
LINE_COLOR = (0.90, 0.90, 0.90, 0.5)

PLAYER_CUE_COLORS = (
    (0.30, 0.72, 1.00, 1.0),
    (1.00, 0.38, 0.32, 1.0),
)
PLAYER_AIM_COLORS = (
    (0.55, 0.88, 1.00, 1.0),
    (1.00, 0.68, 0.55, 1.0),
)


def create_circle_geometry(num_segments: int = 36) -> np.ndarray:
    """Gera vértices para leque de triângulos (TRIANGLE_FAN) com raio unitário centrado na origem."""
    vertices = [[0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    for i in range(num_segments + 1):
        angle = (2.0 * pi * i) / num_segments
        x = cos(angle)
        y = sin(angle)
        vertices.append([x, y, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    return np.array(vertices, dtype="f4").ravel()


def create_ring_geometry(num_segments: int = 36) -> np.ndarray:
    """Gera vértices de circunferência unitária para renderização com LINE_LOOP."""
    vertices = []
    for i in range(num_segments):
        angle = (2.0 * pi * i) / num_segments
        vertices.append([cos(angle), sin(angle), 0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    return np.array(vertices, dtype="f4").ravel()


def create_unit_quad_geometry() -> tuple[np.ndarray, np.ndarray]:
    """Gera um quadrado unitário centrado na origem para barras e ícones geométricos do HUD."""
    vertices = np.array(
        [
            [-0.5, -0.5, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [0.5, -0.5, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [0.5, 0.5, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [-0.5, 0.5, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        ],
        dtype="f4",
    ).ravel()
    indices = np.array([0, 1, 2, 2, 3, 0], dtype="u4")
    return vertices, indices


def create_table_geometry() -> tuple[np.ndarray, np.ndarray]:
    """Gera os vértices e índices (EBO) da área de feltro e das 4 tabelas de madeira (TRIANGLES)."""
    lx, ly = TABLE_WIDTH, TABLE_HEIGHT
    bx, by = TABLE_WIDTH + CUSHION_THICKNESS, TABLE_HEIGHT + CUSHION_THICKNESS

    wood_color = WOOD_COLOR
    felt_color = (1.0, 1.0, 1.0, 1.0)

    vertices = np.array(
        [
            [-lx, -ly, 0.0, 1.0, *felt_color],
            [lx, -ly, 0.0, 1.0, *felt_color],
            [lx, ly, 0.0, 1.0, *felt_color],
            [-lx, ly, 0.0, 1.0, *felt_color],
            [-bx, -by, 0.0, 1.0, *wood_color],
            [bx, -by, 0.0, 1.0, *wood_color],
            [bx, by, 0.0, 1.0, *wood_color],
            [-bx, by, 0.0, 1.0, *wood_color],
        ],
        dtype="f4",
    ).ravel()

    indices = np.array(
        [
            [0, 1, 2, 2, 3, 0],
            [4, 5, 1, 1, 0, 4],
            [3, 2, 6, 6, 7, 3],
            [4, 0, 3, 3, 7, 4],
            [1, 5, 6, 6, 2, 1],
        ],
        dtype="u4",
    ).ravel()

    return vertices, indices


def create_table_lines() -> np.ndarray:
    """Gera a linha de saída e o semicírculo de baulk ('D' de sinuca) com primitiva de linha."""
    x_baulk = -0.45
    r_d = 0.18
    vertices = [
        [x_baulk, -TABLE_HEIGHT, 0.0, 1.0, *LINE_COLOR],
        [x_baulk, TABLE_HEIGHT, 0.0, 1.0, *LINE_COLOR],
    ]

    segments = 24
    for i in range(segments + 1):
        angle = (pi / 2.0) + (pi * i) / segments
        x = x_baulk + r_d * cos(angle)
        y = r_d * sin(angle)
        vertices.append([x, y, 0.0, 1.0, *LINE_COLOR])

    return np.array(vertices, dtype="f4").ravel()


def create_aim_line_geometry(length: float = 1.0, num_dashes: int = 12) -> np.ndarray:
    """Gera segmentos tracejados normalizados (LINES) ao longo do eixo +X para escalonamento via uniform."""
    vertices: list[list[float]] = []
    dash_len = length / (num_dashes * 1.6)
    gap_len = dash_len * 0.6
    aim_color = (1.0, 1.0, 1.0, 0.90)

    x_cur = 0.0
    for _ in range(num_dashes):
        x_next = min(length, x_cur + dash_len)
        vertices.append([x_cur, 0.0, 0.0, 1.0, *aim_color])
        vertices.append([x_next, 0.0, 0.0, 1.0, *aim_color])
        x_cur = x_next + gap_len

    return np.array(vertices, dtype="f4").ravel()


def create_cue_geometry() -> tuple[np.ndarray, np.ndarray]:
    """Gera a malha cônica estática do taco em luminância neutra para modulação de cor por jogador."""
    x_tip = -(BALL_RADIUS + 0.025)
    x_mid = x_tip - 0.22
    x_base = x_tip - 0.50

    w_tip = 0.005
    w_mid = 0.008
    w_base = 0.013

    tip_color = (1.00, 1.00, 1.00, 1.0)
    mid_color = (0.88, 0.85, 0.80, 1.0)
    base_color = (0.42, 0.40, 0.38, 1.0)

    vertices = np.array(
        [
            [x_tip, -w_tip, 0.0, 1.0, *tip_color],
            [x_tip, w_tip, 0.0, 1.0, *tip_color],
            [x_mid, w_mid, 0.0, 1.0, *mid_color],
            [x_mid, -w_mid, 0.0, 1.0, *mid_color],
            [x_mid, -w_mid, 0.0, 1.0, *mid_color],
            [x_mid, w_mid, 0.0, 1.0, *mid_color],
            [x_base, w_base, 0.0, 1.0, *base_color],
            [x_base, -w_base, 0.0, 1.0, *base_color],
        ],
        dtype="f4",
    ).ravel()

    indices = np.array([[0, 1, 2, 2, 3, 0], [4, 5, 6, 6, 7, 4]], dtype="u4").ravel()

    return vertices, indices


def _create_vao(
    ctx: moderngl.Context, prog: moderngl.Program, verts: np.ndarray
) -> tuple[moderngl.Buffer, moderngl.VertexArray]:
    """Cria um VBO estático e um VAO de atributos pos+cor (4f 4f)."""
    vbo = ctx.buffer(verts.tobytes())
    vao = ctx.vertex_array(prog, [(vbo, "4f 4f", "v_position", "v_color")])
    return vbo, vao


def _create_indexed_vao(
    ctx: moderngl.Context,
    prog: moderngl.Program,
    verts: np.ndarray,
    indices: np.ndarray,
) -> tuple[moderngl.Buffer, moderngl.Buffer, moderngl.VertexArray]:
    """Cria um VBO estático, um EBO e um VAO indexado de atributos pos+cor (4f 4f)."""
    vbo = ctx.buffer(verts.tobytes())
    ebo = ctx.buffer(indices.tobytes())
    vao = ctx.vertex_array(prog, [(vbo, "4f 4f", "v_position", "v_color")], index_buffer=ebo)
    return vbo, ebo, vao


def setup_graphics(ctx: moderngl.Context) -> dict[str, Any]:
    """Compila os shaders e inicializa estaticamente todos os VBOs, EBOs e VAOs da cena."""
    prog = create_program(ctx, SHADERS_DIR / "shader.vert", SHADERS_DIR / "shader.frag")

    table_verts, table_indices = create_table_geometry()
    vbo_table, ebo_table, vao_table = _create_indexed_vao(ctx, prog, table_verts, table_indices)

    circle_verts = create_circle_geometry()
    vbo_circle, vao_circle = _create_vao(ctx, prog, circle_verts)

    ring_verts = create_ring_geometry()
    vbo_ring, vao_ring = _create_vao(ctx, prog, ring_verts)

    quad_verts, quad_indices = create_unit_quad_geometry()
    vbo_quad, ebo_quad, vao_quad = _create_indexed_vao(ctx, prog, quad_verts, quad_indices)

    line_verts = create_table_lines()
    vbo_lines, vao_lines = _create_vao(ctx, prog, line_verts)

    aim_verts = create_aim_line_geometry()
    vbo_aim, vao_aim = _create_vao(ctx, prog, aim_verts)

    cue_verts, cue_indices = create_cue_geometry()
    vbo_cue, ebo_cue, vao_cue = _create_indexed_vao(ctx, prog, cue_verts, cue_indices)

    return {
        "prog": prog,
        "vao_table": vao_table,
        "vbo_table": vbo_table,
        "ebo_table": ebo_table,
        "vao_circle": vao_circle,
        "vbo_circle": vbo_circle,
        "circle_count": len(circle_verts) // 8,
        "vao_ring": vao_ring,
        "vbo_ring": vbo_ring,
        "ring_count": len(ring_verts) // 8,
        "vao_quad": vao_quad,
        "vbo_quad": vbo_quad,
        "ebo_quad": ebo_quad,
        "vao_lines": vao_lines,
        "vbo_lines": vbo_lines,
        "line_count": len(line_verts) // 8,
        "vao_aim": vao_aim,
        "vbo_aim": vbo_aim,
        "aim_count": len(aim_verts) // 8,
        "vao_cue": vao_cue,
        "vbo_cue": vbo_cue,
        "ebo_cue": ebo_cue,
    }


def _draw_table(
    prog: moderngl.Program, vao_table: moderngl.VertexArray, felt_color: tuple[float, ...]
) -> None:
    """Renderiza a geometria da mesa de sinuca com a cor do feltro configurada."""
    _set_uniform(prog, "u_offset", (0.0, 0.0))
    _set_uniform(prog, "u_scale", 1.0)
    _set_uniform(prog, "u_color", felt_color)
    vao_table.render(moderngl.TRIANGLES)


def _draw_table_lines(prog: moderngl.Program, vao_lines: moderngl.VertexArray) -> None:
    """Renderiza as marcações de baulk e saída com primitiva LINE_STRIP."""
    _set_uniform(prog, "u_color", (1.0, 1.0, 1.0, 1.0))
    vao_lines.render(moderngl.LINE_STRIP)


def _draw_pockets(
    prog: moderngl.Program,
    vao_circle: moderngl.VertexArray,
    circle_count: int,
    vao_ring: moderngl.VertexArray,
    ring_count: int,
    anim_time: float,
) -> None:
    """Renderiza as 6 caçapas e seus anéis luminosos com pulsação autônoma no tempo."""
    pocket_color = (0.04, 0.04, 0.05, 1.0)
    _set_uniform(prog, "u_scale", POCKET_RADIUS)
    _set_uniform(prog, "u_color", pocket_color)
    for pocket_pos in POCKET_POSITIONS:
        _set_uniform(prog, "u_offset", pocket_pos)
        vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)

    pulse = 0.5 + 0.5 * sin(anim_time * 3.2)
    rim_scale = POCKET_RADIUS * (1.02 + 0.08 * pulse)
    rim_color = (0.95, 0.78, 0.25, 0.55 + 0.35 * pulse)
    _set_uniform(prog, "u_scale", rim_scale)
    _set_uniform(prog, "u_color", rim_color)
    for pocket_pos in POCKET_POSITIONS:
        _set_uniform(prog, "u_offset", pocket_pos)
        vao_ring.render(moderngl.LINE_LOOP, vertices=ring_count)


def _draw_balls(
    prog: moderngl.Program,
    vao_circle: moderngl.VertexArray,
    circle_count: int,
    balls: list[dict[str, Any]],
) -> None:
    """Renderiza todas as bolas ativas em suas posições atuais com suas respectivas cores."""
    _set_uniform(prog, "u_scale", BALL_RADIUS)
    for ball in balls:
        if ball.get("pocketed", False):
            continue
        _set_uniform(prog, "u_offset", tuple(ball["pos"]))
        _set_uniform(prog, "u_color", ball["color"])
        vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)


def _draw_cue_and_aim(
    prog: moderngl.Program,
    pipeline: dict[str, Any],
    cue: dict[str, Any],
    cue_ball_pos: list[float],
    current_player: int,
    anim_time: float,
) -> None:
    """Renderiza a linha de mira, a Ghost Ball pulsante e o taco com a cor exclusiva do jogador da vez."""
    p_idx = (current_player - 1) % 2
    cue_color = PLAYER_CUE_COLORS[p_idx]
    aim_color = PLAYER_AIM_COLORS[p_idx]

    angle = float(cue.get("angle", 0.0))
    power = float(cue.get("power", 0.0))
    aim_dist = max(0.08, float(cue.get("aim_distance", 0.45)) - BALL_RADIUS)
    dir_x, dir_y = cos(angle), sin(angle)

    aim_start = (
        cue_ball_pos[0] + dir_x * (BALL_RADIUS + 0.01),
        cue_ball_pos[1] + dir_y * (BALL_RADIUS + 0.01),
    )
    _set_uniform(prog, "u_angle", angle)
    _set_uniform(prog, "u_offset", aim_start)
    _set_uniform(prog, "u_scale", aim_dist)
    _set_uniform(prog, "u_color", aim_color)
    pipeline["vao_aim"].render(moderngl.LINES, vertices=pipeline["aim_count"])

    pullback = power * 0.16
    cue_offset = (
        cue_ball_pos[0] - dir_x * pullback,
        cue_ball_pos[1] - dir_y * pullback,
    )
    _set_uniform(prog, "u_offset", cue_offset)
    _set_uniform(prog, "u_scale", 1.0)
    _set_uniform(prog, "u_color", cue_color)
    pipeline["vao_cue"].render(moderngl.TRIANGLES)

    ghost_pos = cue.get("ghost_pos")
    if isinstance(ghost_pos, (tuple, list)) and len(ghost_pos) == 2:
        pulse = 0.5 + 0.5 * sin(anim_time * 6.0)
        ghost_scale = BALL_RADIUS * (0.92 + 0.16 * pulse)
        has_target = cue.get("hit_normal") is not None
        ghost_color = (0.30, 1.0, 0.55, 1.0) if has_target else aim_color
        _set_uniform(prog, "u_angle", 0.0)
        _set_uniform(prog, "u_offset", (float(ghost_pos[0]), float(ghost_pos[1])))
        _set_uniform(prog, "u_scale", ghost_scale)
        _set_uniform(prog, "u_color", ghost_color)
        pipeline["vao_ring"].render(moderngl.LINE_LOOP, vertices=pipeline["ring_count"])

        hit_normal = cue.get("hit_normal")
        if isinstance(hit_normal, (tuple, list)) and len(hit_normal) == 2:
            norm_angle = atan2(float(hit_normal[1]), float(hit_normal[0]))
            _set_uniform(prog, "u_angle", norm_angle)
            _set_uniform(prog, "u_offset", (float(ghost_pos[0]), float(ghost_pos[1])))
            _set_uniform(prog, "u_scale", 0.14)
            _set_uniform(prog, "u_color", (0.30, 1.0, 0.55, 1.0))
            pipeline["vao_aim"].render(moderngl.LINES, vertices=pipeline["aim_count"])

    _set_uniform(prog, "u_angle", 0.0)


def _draw_hud(
    prog: moderngl.Program,
    pipeline: dict[str, Any],
    game_state: dict[str, Any],
    cue: dict[str, Any] | None,
    anim_time: float,
) -> None:
    """Renderiza o placar multiplayer (P1 vs P2), emblema de turno ativo, vidas e barra de força."""
    vao_circle = pipeline["vao_circle"]
    circle_count = pipeline["circle_count"]
    vao_ring = pipeline["vao_ring"]
    ring_count = pipeline["ring_count"]
    vao_quad = pipeline["vao_quad"]

    hud_y = 0.62
    bottom_y = -0.62
    slot_radius = 0.017
    slot_step = 0.042
    cur_player = int(game_state.get("current_player", 1))
    pulse = 0.5 + 0.5 * sin(anim_time * 5.0)
    player_racks: list[list[tuple[float, ...]]] = game_state.get(
        "player_pocketed_colors", [[], []]
    )

    _set_uniform(prog, "u_angle", 0.0)

    p1_badge_pos = (-0.92, hud_y)
    _set_uniform(prog, "u_offset", p1_badge_pos)
    _set_uniform(prog, "u_scale", 0.025)
    _set_uniform(prog, "u_color", PLAYER_CUE_COLORS[0])
    vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)
    if cur_player == 1:
        _set_uniform(prog, "u_scale", 0.032 + 0.005 * pulse)
        _set_uniform(prog, "u_color", (1.0, 1.0, 1.0, 1.0))
        vao_ring.render(moderngl.LINE_LOOP, vertices=ring_count)

    for i in range(8):
        pos = (-0.84 + i * slot_step, hud_y)
        _set_uniform(prog, "u_offset", pos)
        if i < len(player_racks[0]):
            _set_uniform(prog, "u_scale", slot_radius)
            _set_uniform(prog, "u_color", player_racks[0][i])
            vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)
        else:
            _set_uniform(prog, "u_scale", slot_radius * 0.85)
            _set_uniform(prog, "u_color", (0.40, 0.55, 0.72, 0.65))
            vao_ring.render(moderngl.LINE_LOOP, vertices=ring_count)

    p2_badge_pos = (0.92, hud_y)
    _set_uniform(prog, "u_offset", p2_badge_pos)
    _set_uniform(prog, "u_scale", 0.025)
    _set_uniform(prog, "u_color", PLAYER_CUE_COLORS[1])
    vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)
    if cur_player == 2:
        _set_uniform(prog, "u_scale", 0.032 + 0.005 * pulse)
        _set_uniform(prog, "u_color", (1.0, 1.0, 1.0, 1.0))
        vao_ring.render(moderngl.LINE_LOOP, vertices=ring_count)

    for i in range(8):
        pos = (0.84 - i * slot_step, hud_y)
        _set_uniform(prog, "u_offset", pos)
        if i < len(player_racks[1]):
            _set_uniform(prog, "u_scale", slot_radius)
            _set_uniform(prog, "u_color", player_racks[1][i])
            vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)
        else:
            _set_uniform(prog, "u_scale", slot_radius * 0.85)
            _set_uniform(prog, "u_color", (0.72, 0.45, 0.42, 0.65))
            vao_ring.render(moderngl.LINE_LOOP, vertices=ring_count)

    lives = int(game_state.get("lives", 3))
    life_radius = 0.019
    for i in range(3):
        pos = (-0.86 + i * 0.052, bottom_y)
        _set_uniform(prog, "u_offset", pos)
        if i < lives:
            _set_uniform(prog, "u_scale", life_radius)
            _set_uniform(prog, "u_color", (0.96, 0.96, 0.96, 1.0))
            vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)
        else:
            _set_uniform(prog, "u_scale", life_radius)
            _set_uniform(prog, "u_color", (0.85, 0.20, 0.20, 0.8))
            vao_ring.render(moderngl.LINE_LOOP, vertices=ring_count)

    power = float(cue.get("power", 0.0)) if cue else 0.0
    bar_segments = 10
    seg_size = 0.018
    bar_start_x = 0.62
    active_segs = int(round(power * bar_segments))
    for i in range(bar_segments):
        pos = (bar_start_x + i * 0.025, bottom_y)
        _set_uniform(prog, "u_offset", pos)
        _set_uniform(prog, "u_scale", seg_size)
        if i < active_segs:
            t = i / max(1, bar_segments - 1)
            seg_color = (0.20 + 0.75 * t, 0.85 - 0.65 * t, 0.20, 1.0)
            _set_uniform(prog, "u_color", seg_color)
        else:
            _set_uniform(prog, "u_color", (0.28, 0.30, 0.34, 0.7))
        vao_quad.render(moderngl.TRIANGLES)

    state = game_state.get("state", "PLAYING")
    if state == "PAUSED":
        for dx in (-0.022, 0.022):
            for dy in (-0.015, 0.0, 0.015):
                _set_uniform(prog, "u_offset", (dx, hud_y + dy))
                _set_uniform(prog, "u_scale", 0.018)
                _set_uniform(prog, "u_color", (0.98, 0.80, 0.15, 1.0))
                vao_quad.render(moderngl.TRIANGLES)
    elif state in ("VICTORY", "GAME_OVER"):
        winner = int(game_state.get("winner", 1))
        win_color = PLAYER_CUE_COLORS[(winner - 1) % 2]
        _set_uniform(prog, "u_offset", (0.0, hud_y))
        _set_uniform(prog, "u_scale", 0.032 + 0.008 * pulse)
        _set_uniform(prog, "u_color", win_color)
        vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)
    elif state == "START":
        _set_uniform(prog, "u_offset", (0.0, hud_y))
        _set_uniform(prog, "u_scale", 0.024 + 0.006 * pulse)
        _set_uniform(prog, "u_color", PLAYER_CUE_COLORS[(cur_player - 1) % 2])
        vao_ring.render(moderngl.LINE_LOOP, vertices=ring_count)


def get_projection_scale(window: Any) -> tuple[float, float]:
    """Calcula os fatores de projeção (sx, sy) para ajustar a cena e o HUD sem distorção."""
    width, height = glfw.get_framebuffer_size(window)
    if width <= 0 or height <= 0:
        return 1.0, 1.0
    aspect = width / height
    sy = min(1.42, 0.96 * aspect)
    sx = sy / aspect
    return sx, sy


def render_scene(
    ctx: moderngl.Context,
    pipeline: dict[str, Any],
    balls: list[dict[str, Any]],
    proj_scale: tuple[float, float] | float = (1.0, 1.0),
    cue: dict[str, Any] | None = None,
    felt_color_index: int = 0,
    night_mode: bool = False,
    game_state: dict[str, Any] | None = None,
    anim_time: float = 0.0,
) -> None:
    """Renderiza a cena completa de sinuca, taco colorido por jogador, animações e HUD."""
    prog = pipeline["prog"]
    bg_color = (0.05, 0.05, 0.08, 1.0) if night_mode else (0.82, 0.82, 0.85, 1.0)
    attenuation = 0.40 if night_mode else 1.0
    felt_color = FELT_COLORS[felt_color_index % len(FELT_COLORS)]
    cur_player = int(game_state.get("current_player", 1)) if game_state else 1

    ctx.clear(*bg_color)

    scale_vec = (
        tuple(proj_scale) if isinstance(proj_scale, (tuple, list)) else (1.0 / proj_scale, 1.0)
    )
    _set_uniform(prog, "u_proj", scale_vec)
    _set_uniform(prog, "u_attenuation", attenuation)
    _set_uniform(prog, "u_angle", 0.0)

    _draw_table(prog, pipeline["vao_table"], felt_color)
    _draw_table_lines(prog, pipeline["vao_lines"])
    _draw_pockets(
        prog,
        pipeline["vao_circle"],
        pipeline["circle_count"],
        pipeline["vao_ring"],
        pipeline["ring_count"],
        anim_time,
    )
    _draw_balls(prog, pipeline["vao_circle"], pipeline["circle_count"], balls)

    if cue and cue.get("visible", False):
        _draw_cue_and_aim(prog, pipeline, cue, balls[0]["pos"], cur_player, anim_time)

    if game_state is not None:
        _draw_hud(prog, pipeline, game_state, cue, anim_time)


def main() -> None:
    """Executa a suíte de testes unitários do pipeline gráfico multiplayer do Sinucadas."""
    import math
    import os
    from unittest.mock import MagicMock

    assert _resolve_shader_code(None) is None
    dummy_shader = "#version 330 core\nvoid main() { gl_Position = vec4(0.0); }"
    assert _resolve_shader_code(dummy_shader) == dummy_shader

    dummy_win = MagicMock()
    orig_fb = glfw.get_framebuffer_size
    try:
        glfw.get_framebuffer_size = MagicMock(return_value=(800, 600))
        sx, sy = get_projection_scale(dummy_win)
        assert math.isclose(sx, 0.96)
        assert math.isclose(sy, 0.96 * (800 / 600))

        glfw.get_framebuffer_size = MagicMock(return_value=(0, 0))
        assert get_projection_scale(dummy_win) == (1.0, 1.0)
    finally:
        glfw.get_framebuffer_size = orig_fb

    test_ctx: moderngl.Context | None = None
    headless_win = None
    try:
        test_ctx = moderngl.create_context(standalone=True)
    except Exception:
        try:
            test_ctx = moderngl.create_context(standalone=True, backend="egl")  # type: ignore[arg-type]
        except Exception:
            pass

    if test_ctx is None and (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        if glfw.init():
            glfw.window_hint(glfw.VISIBLE, False)
            headless_win = glfw.create_window(100, 100, "HeadlessTest", None, None)
            if headless_win:
                glfw.make_context_current(headless_win)
                try:
                    test_ctx = moderngl.create_context()
                except Exception:
                    pass

    if test_ctx is not None:
        pipeline = setup_graphics(test_ctx)
        assert "prog" in pipeline
        assert "vao_circle" in pipeline
        assert "vao_ring" in pipeline
        assert "vao_quad" in pipeline
        assert "vao_table" in pipeline

        test_balls = [{"pos": [-0.45, 0.0], "color": (1.0, 1.0, 1.0, 1.0), "pocketed": False}]
        test_cue = {
            "angle": 0.0,
            "power": 0.5,
            "visible": True,
            "aim_distance": 0.4,
            "ghost_pos": (0.0, 0.0),
            "hit_normal": (1.0, 0.0),
        }
        test_state = {
            "state": "PLAYING",
            "current_player": 2,
            "scores": [12, 8],
            "balls_pocketed": [1, 1],
            "player_pocketed_colors": [[(1.0, 0.0, 0.0, 1.0)], [(0.0, 1.0, 0.0, 1.0)]],
            "lives": 3,
            "score": 2,
        }
        render_scene(
            test_ctx,
            pipeline,
            test_balls,
            proj_scale=(1.0, 1.0),
            cue=test_cue,
            game_state=test_state,
            anim_time=1.0,
        )

        for v in pipeline.values():
            if hasattr(v, "release"):
                v.release()
        test_ctx.release()
        if headless_win:
            glfw.destroy_window(headless_win)
            glfw.terminate()
        print(
            "graphics.py: shader resolution, player cue colors, static VBOs, and HUD validated successfully."
        )
    else:
        print(
            "graphics.py: shader resolution and math validated; ModernGL context test skipped (headless environment)."
        )


if __name__ == "__main__":
    main()
