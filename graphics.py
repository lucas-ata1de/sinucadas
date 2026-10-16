#!/usr/bin/env python3
"""
Módulo de renderização e primitivas gráficas do Sinucadas.
Gerencia a compilação dos shaders, geometria da mesa, caçapas, bolas e linhas da quadra.
Utiliza múltiplas primitivas (TRIANGLES, TRIANGLE_FAN, LINE_STRIP) e reaproveita buffers.
"""

from math import cos, pi, sin
from pathlib import Path
from typing import Any, cast

import moderngl
import numpy as np

from environment import create_program


def set_uniform(prog: moderngl.Program, name: str, value: Any) -> None:
    """Atualiza o valor de um uniforme no programa GLSL com tipagem estática segura."""
    cast(moderngl.Uniform, prog[name]).value = value

SHADERS_DIR = Path(__file__).parent / "shaders"

MESA_LARGURA = 0.90
MESA_ALTURA = 0.45
BORDA_ESPESSURA = 0.10

POSICOES_CACAPAS = (
    (-0.88, -0.43),
    (0.00, -0.45),
    (0.88, -0.43),
    (-0.88, 0.43),
    (0.00, 0.45),
    (0.88, 0.43),
)

RAIO_CACAPA = 0.055
RAIO_BOLA = 0.032

CORES_FELTRO = (
    (0.10, 0.52, 0.24, 1.0),
    (0.12, 0.38, 0.65, 1.0),
    (0.55, 0.12, 0.18, 1.0),
    (0.16, 0.18, 0.20, 1.0),
)

COR_MADEIRA = (0.35, 0.18, 0.08, 1.0)
COR_BORDA_INTERNA = (0.22, 0.11, 0.05, 1.0)
COR_LINHA = (0.90, 0.90, 0.90, 0.5)


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
    lx, ly = MESA_LARGURA, MESA_ALTURA
    bx, by = MESA_LARGURA + BORDA_ESPESSURA, MESA_ALTURA + BORDA_ESPESSURA

    c_m = COR_MADEIRA
    c_f = (1.0, 1.0, 1.0, 1.0)

    vertices = [
        [-lx, -ly, 0.0, 1.0, *c_f],
        [lx, -ly, 0.0, 1.0, *c_f],
        [lx, ly, 0.0, 1.0, *c_f],
        [-lx, ly, 0.0, 1.0, *c_f],
        [-bx, -by, 0.0, 1.0, *c_m],
        [bx, -by, 0.0, 1.0, *c_m],
        [bx, by, 0.0, 1.0, *c_m],
        [-bx, by, 0.0, 1.0, *c_m],
    ]

    indices = [
        0,
        1,
        2,
        2,
        3,
        0,
        4,
        5,
        1,
        1,
        0,
        4,
        3,
        2,
        6,
        6,
        7,
        3,
        4,
        0,
        3,
        3,
        7,
        4,
        1,
        5,
        6,
        6,
        2,
        1,
    ]

    return np.array(vertices, dtype="f4").ravel(), np.array(indices, dtype="u4")


def create_table_lines() -> np.ndarray:
    """Gera a linha de saída e o semicírculo de baulk ('D' de sinuca) com primitiva de linha."""
    x_baulk = -0.45
    r_d = 0.18
    vertices = [
        [x_baulk, -MESA_ALTURA, 0.0, 1.0, *COR_LINHA],
        [x_baulk, MESA_ALTURA, 0.0, 1.0, *COR_LINHA],
    ]

    segments = 24
    for i in range(segments + 1):
        angle = (pi / 2.0) + (pi * i) / segments
        x = x_baulk + r_d * cos(angle)
        y = r_d * sin(angle)
        vertices.append([x, y, 0.0, 1.0, *COR_LINHA])

    return np.array(vertices, dtype="f4").ravel()


def create_aim_line_geometry(length: float = 0.45, num_dashes: int = 8) -> np.ndarray:
    """Gera segmentos tracejados para a linha guia de mira (LINES) à frente da bola branca."""
    vertices: list[list[float]] = []
    dash_len = length / (num_dashes * 1.6)
    gap_len = dash_len * 0.6
    cor_mira = (1.0, 1.0, 0.65, 0.75)

    x_cur = RAIO_BOLA + 0.015
    for _ in range(num_dashes):
        x_next = x_cur + dash_len
        vertices.append([x_cur, 0.0, 0.0, 1.0, *cor_mira])
        vertices.append([x_next, 0.0, 0.0, 1.0, *cor_mira])
        x_cur = x_next + gap_len

    return np.array(vertices, dtype="f4").ravel()


def create_cue_geometry(power: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Gera a malha cônica do taco de sinuca (TRIANGLES com EBO) com recuo proporcional à força."""
    x_tip = -(RAIO_BOLA + 0.025 + power * 0.16)
    x_mid = x_tip - 0.22
    x_base = x_tip - 0.50

    w_tip = 0.005
    w_mid = 0.008
    w_base = 0.013

    c_tip = (0.92, 0.92, 0.96, 1.0)
    c_mid = (0.75, 0.50, 0.22, 1.0)
    c_base = (0.28, 0.14, 0.05, 1.0)

    vertices = [
        [x_tip, -w_tip, 0.0, 1.0, *c_tip],
        [x_tip, w_tip, 0.0, 1.0, *c_tip],
        [x_mid, w_mid, 0.0, 1.0, *c_mid],
        [x_mid, -w_mid, 0.0, 1.0, *c_mid],
        [x_mid, -w_mid, 0.0, 1.0, *c_mid],
        [x_mid, w_mid, 0.0, 1.0, *c_mid],
        [x_base, w_base, 0.0, 1.0, *c_base],
        [x_base, -w_base, 0.0, 1.0, *c_base],
    ]

    indices = [
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
    ]

    return np.array(vertices, dtype="f4").ravel(), np.array(indices, dtype="u4")


def setup_graphics(ctx: moderngl.Context) -> dict[str, Any]:
    """Compila os shaders e inicializa todos os VBOs, EBOs e VAOs da cena."""
    prog = create_program(ctx, SHADERS_DIR / "shader.vert", SHADERS_DIR / "shader.frag")

    table_verts, table_indices = create_table_geometry()
    vbo_table = ctx.buffer(table_verts.tobytes())
    ebo_table = ctx.buffer(table_indices.tobytes())
    vao_table = ctx.vertex_array(
        prog,
        [(vbo_table, "4f 4f", "v_position", "v_color")],
        index_buffer=ebo_table,
    )

    circle_verts = create_circle_geometry(num_segments=36)
    vbo_circle = ctx.buffer(circle_verts.tobytes())
    vao_circle = ctx.vertex_array(
        prog,
        [(vbo_circle, "4f 4f", "v_position", "v_color")],
    )

    line_verts = create_table_lines()
    vbo_lines = ctx.buffer(line_verts.tobytes())
    vao_lines = ctx.vertex_array(
        prog,
        [(vbo_lines, "4f 4f", "v_position", "v_color")],
    )

    aim_verts = create_aim_line_geometry()
    vbo_aim = ctx.buffer(aim_verts.tobytes())
    vao_aim = ctx.vertex_array(
        prog,
        [(vbo_aim, "4f 4f", "v_position", "v_color")],
    )

    cue_verts, cue_indices = create_cue_geometry(0.0)
    vbo_cue = ctx.buffer(cue_verts.tobytes(), dynamic=True)
    ebo_cue = ctx.buffer(cue_indices.tobytes())
    vao_cue = ctx.vertex_array(
        prog,
        [(vbo_cue, "4f 4f", "v_position", "v_color")],
        index_buffer=ebo_cue,
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


def render_scene(
    ctx: moderngl.Context,
    pipeline: dict[str, Any],
    balls: list[dict[str, Any]],
    proj_scale: tuple[float, float] | float = (1.0, 1.0),
    cue: dict[str, Any] | None = None,
    felt_color_index: int = 0,
    night_mode: bool = False,
) -> None:
    """Renderiza a cena completa de sinuca com projeção isotrópica e atenuação de iluminação."""
    prog = pipeline["prog"]

    bg_color = (0.05, 0.05, 0.08, 1.0) if night_mode else (0.82, 0.82, 0.85, 1.0)
    attenuation = 0.40 if night_mode else 1.0
    felt_color = CORES_FELTRO[felt_color_index % len(CORES_FELTRO)]

    ctx.clear(*bg_color)

    scale_vec = (
        (proj_scale[0], proj_scale[1])
        if isinstance(proj_scale, (tuple, list))
        else (1.0 / proj_scale, 1.0)
    )
    set_uniform(prog, "u_proj", scale_vec)
    set_uniform(prog, "u_attenuation", attenuation)
    set_uniform(prog, "u_angle", 0.0)

    set_uniform(prog, "u_offset", (0.0, 0.0))
    set_uniform(prog, "u_scale", 1.0)
    set_uniform(prog, "u_color", felt_color)
    pipeline["vao_table"].render(moderngl.TRIANGLES)

    set_uniform(prog, "u_color", (1.0, 1.0, 1.0, 1.0))
    pipeline["vao_lines"].render(moderngl.LINE_STRIP)

    cor_cacapa = (0.04, 0.04, 0.05, 1.0)
    set_uniform(prog, "u_scale", RAIO_CACAPA)
    set_uniform(prog, "u_color", cor_cacapa)
    for px, py in POSICOES_CACAPAS:
        set_uniform(prog, "u_offset", (px, py))
        pipeline["vao_circle"].render(
            moderngl.TRIANGLE_FAN, vertices=pipeline["circle_count"]
        )

    set_uniform(prog, "u_scale", RAIO_BOLA)
    for ball in balls:
        if ball.get("pocketed", False):
            continue
        set_uniform(prog, "u_offset", tuple(ball["pos"]))
        set_uniform(prog, "u_color", ball["color"])
        pipeline["vao_circle"].render(
            moderngl.TRIANGLE_FAN, vertices=pipeline["circle_count"]
        )

    if cue and cue.get("visible", False):
        cue_verts, _ = create_cue_geometry(cue.get("power", 0.0))
        pipeline["vbo_cue"].write(cue_verts.tobytes())

        set_uniform(prog, "u_angle", cue.get("angle", 0.0))
        set_uniform(prog, "u_offset", tuple(balls[0]["pos"]))
        set_uniform(prog, "u_scale", 1.0)
        set_uniform(prog, "u_color", (1.0, 1.0, 1.0, 1.0))

        pipeline["vao_aim"].render(moderngl.LINES, vertices=pipeline["aim_count"])
        pipeline["vao_cue"].render(moderngl.TRIANGLES)

        set_uniform(prog, "u_angle", 0.0)


if __name__ == "__main__":
    test_ctx = None
    try:
        test_ctx = moderngl.create_context(standalone=True)
    except Exception:
        try:
            test_ctx = moderngl.create_context(standalone=True, backend="egl")  # type: ignore[arg-type]
        except Exception:
            pass

    if test_ctx is not None:
        p = setup_graphics(test_ctx)
        print("graphics.py: shaders compilados e pipeline de múltiplas primitivas inicializado.")
        for k, v in p.items():
            if hasattr(v, "release"):
                v.release()
        test_ctx.release()
    else:
        print("graphics.py: teste de contexto standalone indisponível.")
