#!/usr/bin/env python3
"""
Módulo de renderização e primitivas gráficas do Sinucadas.
Gerencia a compilação dos shaders, geometria da mesa, caçapas, bolas e linhas da quadra.
Utiliza múltiplas primitivas (TRIANGLES, TRIANGLE_FAN, LINE_STRIP) e reaproveita buffers.
"""

import sys
from math import cos, pi, sin
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

COLOR_YELLOW = (0.95, 0.85, 0.15, 1.0)
COLOR_BLUE = (0.15, 0.35, 0.85, 1.0)
COLOR_RED = (0.85, 0.15, 0.15, 1.0)
COLOR_PURPLE = (0.50, 0.15, 0.65, 1.0)
COLOR_ORANGE = (0.95, 0.50, 0.15, 1.0)
COLOR_GREEN = (0.15, 0.65, 0.25, 1.0)
COLOR_BROWN = (0.50, 0.25, 0.15, 1.0)
COLOR_BLACK = (0.10, 0.10, 0.10, 1.0)
COLOR_STRIPED_YELLOW = (0.95, 0.90, 0.50, 1.0)
COLOR_STRIPED_BLUE = (0.45, 0.65, 0.95, 1.0)
COLOR_STRIPED_RED = (0.95, 0.45, 0.45, 1.0)
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


def create_scene_balls() -> list[dict[str, Any]]:
    """Gera as 16 bolas na mesa (bola branca na saída e triângulo no foot spot)."""
    cue_ball = {
        "id": 0,
        "pos": [-0.45, 0.0],
        "color": CUE_BALL_COLOR,
    }
    balls: list[dict[str, Any]] = [cue_ball]
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
                    "id": len(balls),
                    "pos": [col_x, col_y],
                    "color": color,
                }
            )
    return balls


def create_circle_geometry(num_segments: int = 36) -> np.ndarray:
    """Gera vértices para leque de triângulos (TRIANGLE_FAN) com raio unitário centrado na origem."""
    vertices = [[0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    for i in range(num_segments + 1):
        angle = (2.0 * pi * i) / num_segments
        x = cos(angle)
        y = sin(angle)
        vertices.append([x, y, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    return np.array(vertices, dtype="f4").ravel()


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


def create_aim_line_geometry(length: float = 0.45, num_dashes: int = 8) -> np.ndarray:
    """Gera segmentos tracejados para a linha guia de mira (LINES) à frente da bola branca."""
    vertices: list[list[float]] = []
    dash_len = length / (num_dashes * 1.6)
    gap_len = dash_len * 0.6
    aim_color = (1.0, 1.0, 0.65, 0.75)

    x_cur = BALL_RADIUS + 0.015
    for _ in range(num_dashes):
        x_next = x_cur + dash_len
        vertices.append([x_cur, 0.0, 0.0, 1.0, *aim_color])
        vertices.append([x_next, 0.0, 0.0, 1.0, *aim_color])
        x_cur = x_next + gap_len

    return np.array(vertices, dtype="f4").ravel()


def create_cue_geometry(power: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Gera a malha cônica do taco de sinuca (TRIANGLES com EBO) com recuo proporcional à força."""
    x_tip = -(BALL_RADIUS + 0.025 + power * 0.16)
    x_mid = x_tip - 0.22
    x_base = x_tip - 0.50

    w_tip = 0.005
    w_mid = 0.008
    w_base = 0.013

    tip_color = (0.92, 0.92, 0.96, 1.0)
    mid_color = (0.75, 0.50, 0.22, 1.0)
    base_color = (0.28, 0.14, 0.05, 1.0)

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
    """Cria um VBO e um VAO de atributos pos+cor (4f 4f)."""
    vbo = ctx.buffer(verts.tobytes())
    vao = ctx.vertex_array(prog, [(vbo, "4f 4f", "v_position", "v_color")])
    return vbo, vao


def _create_indexed_vao(
    ctx: moderngl.Context,
    prog: moderngl.Program,
    verts: np.ndarray,
    indices: np.ndarray,
    dynamic: bool = False,
) -> tuple[moderngl.Buffer, moderngl.Buffer, moderngl.VertexArray]:
    """Cria um VBO, um EBO e um VAO indexado de atributos pos+cor (4f 4f)."""
    vbo = ctx.buffer(verts.tobytes(), dynamic=dynamic)
    ebo = ctx.buffer(indices.tobytes())
    vao = ctx.vertex_array(prog, [(vbo, "4f 4f", "v_position", "v_color")], index_buffer=ebo)
    return vbo, ebo, vao


def setup_graphics(ctx: moderngl.Context) -> dict[str, Any]:
    """Compila os shaders e inicializa todos os VBOs, EBOs e VAOs da cena."""
    prog = create_program(ctx, SHADERS_DIR / "shader.vert", SHADERS_DIR / "shader.frag")

    table_verts, table_indices = create_table_geometry()
    vbo_table, ebo_table, vao_table = _create_indexed_vao(ctx, prog, table_verts, table_indices)

    circle_verts = create_circle_geometry()
    vbo_circle, vao_circle = _create_vao(ctx, prog, circle_verts)

    line_verts = create_table_lines()
    vbo_lines, vao_lines = _create_vao(ctx, prog, line_verts)

    aim_verts = create_aim_line_geometry()
    vbo_aim, vao_aim = _create_vao(ctx, prog, aim_verts)

    cue_verts, cue_indices = create_cue_geometry(0.0)
    vbo_cue, ebo_cue, vao_cue = _create_indexed_vao(
        ctx, prog, cue_verts, cue_indices, dynamic=True
    )

    return {
        "prog": prog,
        "vao_table": vao_table,
        "vbo_table": vbo_table,
        "ebo_table": ebo_table,
        "vao_circle": vao_circle,
        "vbo_circle": vbo_circle,
        "circle_count": len(circle_verts) // 8,
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
    prog: moderngl.Program, vao_circle: moderngl.VertexArray, circle_count: int
) -> None:
    """Renderiza as 6 caçapas da mesa com círculos escurecidos."""
    pocket_color = (0.04, 0.04, 0.05, 1.0)
    _set_uniform(prog, "u_scale", POCKET_RADIUS)
    _set_uniform(prog, "u_color", pocket_color)
    for pocket_pos in POCKET_POSITIONS:
        _set_uniform(prog, "u_offset", pocket_pos)
        vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)


def _draw_balls(
    prog: moderngl.Program,
    vao_circle: moderngl.VertexArray,
    circle_count: int,
    balls: list[dict[str, Any]],
) -> None:
    """Renderiza todas as bolas da cena em suas posições com suas respectivas cores."""
    _set_uniform(prog, "u_scale", BALL_RADIUS)
    for ball in balls:
        _set_uniform(prog, "u_offset", tuple(ball["pos"]))
        _set_uniform(prog, "u_color", ball["color"])
        vao_circle.render(moderngl.TRIANGLE_FAN, vertices=circle_count)


def _draw_cue_and_aim(
    prog: moderngl.Program,
    pipeline: dict[str, Any],
    cue: dict[str, Any],
    cue_ball_pos: list[float],
) -> None:
    """Atualiza a geometria dinâmica do taco e renderiza a linha guia de mira e o taco."""
    cue_verts, _ = create_cue_geometry(cue.get("power", 0.0))
    pipeline["vbo_cue"].write(cue_verts.tobytes())

    _set_uniform(prog, "u_angle", cue.get("angle", 0.0))
    _set_uniform(prog, "u_offset", tuple(cue_ball_pos))
    _set_uniform(prog, "u_scale", 1.0)
    _set_uniform(prog, "u_color", (1.0, 1.0, 1.0, 1.0))

    pipeline["vao_aim"].render(moderngl.LINES, vertices=pipeline["aim_count"])
    pipeline["vao_cue"].render(moderngl.TRIANGLES)
    _set_uniform(prog, "u_angle", 0.0)


def get_projection_scale(window: Any) -> tuple[float, float]:
    """Calcula os fatores de projeção (sx, sy) para ajustar a cena sem distorção e sem transbordar."""
    width, height = glfw.get_framebuffer_size(window)
    if width <= 0 or height <= 0:
        return 1.0, 1.0
    aspect = width / height
    sy = min(1.75, 0.98 * aspect)
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
) -> None:
    """Renderiza a cena completa de sinuca com projeção isotrópica e iluminação modulada."""
    prog = pipeline["prog"]
    bg_color = (0.05, 0.05, 0.08, 1.0) if night_mode else (0.82, 0.82, 0.85, 1.0)
    attenuation = 0.40 if night_mode else 1.0
    felt_color = FELT_COLORS[felt_color_index % len(FELT_COLORS)]

    ctx.clear(*bg_color)

    scale_vec = (
        tuple(proj_scale) if isinstance(proj_scale, (tuple, list)) else (1.0 / proj_scale, 1.0)
    )
    _set_uniform(prog, "u_proj", scale_vec)
    _set_uniform(prog, "u_attenuation", attenuation)
    _set_uniform(prog, "u_angle", 0.0)

    _draw_table(prog, pipeline["vao_table"], felt_color)
    _draw_table_lines(prog, pipeline["vao_lines"])
    _draw_pockets(prog, pipeline["vao_circle"], pipeline["circle_count"])
    _draw_balls(prog, pipeline["vao_circle"], pipeline["circle_count"], balls)

    if cue and cue.get("visible", False):
        _draw_cue_and_aim(prog, pipeline, cue, balls[0]["pos"])


if __name__ == "__main__":
    def _test_graphics_module() -> None:
        import math
        import os
        from unittest.mock import MagicMock

        # 1. Test shader code resolution
        assert _resolve_shader_code(None) is None
        dummy_shader = "#version 330 core\nvoid main() { gl_Position = vec4(0.0); }"
        assert _resolve_shader_code(dummy_shader) == dummy_shader

        # 2. Test initial balls generation
        balls = create_scene_balls()
        assert len(balls) == 16, f"Expected 16 balls, got {len(balls)}"
        assert balls[0]["id"] == 0, "Ball 0 must be cue ball"
        assert all("pos" in b and "color" in b for b in balls)

        # 3. Test get_projection_scale with mocked window
        dummy_win = MagicMock()
        orig_fb = glfw.get_framebuffer_size
        try:
            glfw.get_framebuffer_size = MagicMock(return_value=(800, 600))
            sx, sy = get_projection_scale(dummy_win)
            assert math.isclose(sx, 0.98)
            assert math.isclose(sy, 0.98 * (800 / 600))

            glfw.get_framebuffer_size = MagicMock(return_value=(0, 0))
            assert get_projection_scale(dummy_win) == (1.0, 1.0)
        finally:
            glfw.get_framebuffer_size = orig_fb

        # 4. Test ModernGL context, pipeline setup, and rendering
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
            assert "vao_table" in pipeline

            test_cue = {"angle": 0.0, "power": 0.5, "visible": True}
            render_scene(test_ctx, pipeline, balls, proj_scale=(1.0, 1.0), cue=test_cue)

            for v in pipeline.values():
                if hasattr(v, "release"):
                    v.release()
            test_ctx.release()
            if headless_win:
                glfw.destroy_window(headless_win)
                glfw.terminate()
            print("graphics.py: shader resolution, math, and ModernGL rendering pipeline validated successfully.")
        else:
            print("graphics.py: shader resolution and math validated; ModernGL context test skipped (headless environment).")

    _test_graphics_module()
