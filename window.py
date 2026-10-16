#!/usr/bin/env python3
"""
Gerenciamento de janelas e callbacks de entrada para o Sinucadas.
Trata a criação da janela GLFW, pooling de eventos, troca de buffers e callbacks de janela e teclado.
"""

from typing import Any

import glfw
import moderngl

from environment import adjust_viewport, window_setup


def key_callback(window: Any, key: int, scancode: int, action: int, mods: int) -> None:
    """Callback de teclado que fecha a janela ao pressionar a tecla ESC."""
    if action == glfw.PRESS and key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def init_window(
    size: tuple[int, int] = (800, 600),
    title: str = "Sinucadas",
    enable_hot_reload: bool = True,
) -> tuple[Any, moderngl.Context]:
    """Cria a janela da aplicação e registra os callbacks de entrada e redimensionamento."""
    window, ctx = window_setup(size, title, enable_hot_reload=enable_hot_reload)

    glfw.set_key_callback(window, key_callback)
    glfw.set_framebuffer_size_callback(
        window,
        lambda win, width, height: adjust_viewport(ctx, (width, height)),
    )

    return window, ctx


if __name__ == "__main__":
    win, context = init_window((400, 300), "Teste de Janela")
    print(f"window.py: Contexto OpenGL inicializado ({context.info['GL_RENDERER']}).")
    context.release()
    glfw.terminate()
