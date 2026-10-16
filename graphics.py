#!/usr/bin/env python3
"""
Módulo de renderização e primitivas gráficas do Sinucadas.
Gerencia shaders, buffers de vértices (VBO/EBO), vertex arrays (VAO) e chamadas de desenho.
"""

from pathlib import Path

import moderngl
import numpy as np

from environment import create_program

SHADERS_DIR = Path(__file__).parent / "shaders"


def setup_graphics(
    ctx: moderngl.Context,
) -> tuple[moderngl.Program, moderngl.Buffer, moderngl.Buffer, moderngl.VertexArray]:
    """Compila os shaders e inicializa os buffers e o vertex array da cena."""
    prog = create_program(ctx, SHADERS_DIR / "bola.vert", SHADERS_DIR / "shader.frag")

    vertices = np.array(
        [
            [-0.5,  0.5, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0],
            [-0.5, -0.5, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0],
            [ 0.5, -0.5, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0],
            [ 0.5,  0.5, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0],
        ],
        dtype="f4",
    ).ravel()

    indices = np.array([0, 1, 2, 3, 2, 0], dtype="u4")

    vbo = ctx.buffer(vertices.tobytes())
    ebo = ctx.buffer(indices.tobytes())

    vao = ctx.vertex_array(
        prog,
        [(vbo, "4f 4f", "v_position", "v_color")],
        index_buffer=ebo,
    )

    return prog, vbo, ebo, vao


def render_frame(
    ctx: moderngl.Context,
    prog: moderngl.Program,
    vao: moderngl.VertexArray,
    y_pos: float,
) -> None:
    """Limpa o framebuffer, atualiza uniformes do shader e renderiza o vertex array."""
    ctx.clear(1.0, 1.0, 1.0, 1.0)
    prog["u_offset"].value = (0.0, y_pos)
    prog["u_scale"].value = 0.1
    vao.render(moderngl.TRIANGLES)


if __name__ == "__main__":
    test_ctx = None
    for kwargs in ({}, {"backend": "egl"}):
        try:
            test_ctx = moderngl.create_context(standalone=True, **kwargs)
            break
        except Exception:
            continue

    if test_ctx is not None:
        resources = setup_graphics(test_ctx)
        print("graphics.py: shaders compilados e VAO/VBO/EBO inicializados com sucesso.")
        for res in resources:
            res.release()
        test_ctx.release()
    else:
        print("graphics.py: pulando teste de contexto standalone (nenhum display/EGL disponível).")
