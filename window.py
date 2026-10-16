#!/usr/bin/env python3
"""
Gerenciamento de janelas e callbacks de entrada para o Sinucadas.
Trata a criação da janela GLFW, pooling de eventos, troca de buffers e callbacks de janela e teclado.
"""

from collections.abc import Callable
from typing import Any

import glfw
import moderngl

from environment import adjust_viewport, window_setup


def default_key_callback(
    window: Any, key: int, scancode: int, action: int, mods: int
) -> None:
    """Callback de teclado padrão que fecha a janela ao pressionar a tecla ESC."""
    if action == glfw.PRESS and key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def init_window(
    size: tuple[int, int] = (800, 600),
    title: str = "Sinucadas",
    enable_hot_reload: bool = True,
    user_key_callback: Callable[[Any, int, int, int, int], None] | None = None,
) -> tuple[Any, moderngl.Context]:
    """Cria a janela da aplicação e registra os callbacks de entrada e redimensionamento."""
    window, ctx = window_setup(size, title, enable_hot_reload=enable_hot_reload)

    def on_resize(_win: Any, width: int, height: int) -> None:
        adjust_viewport(ctx, (width, height))

    active_callback = user_key_callback or default_key_callback
    glfw.set_key_callback(window, active_callback)
    glfw.set_framebuffer_size_callback(window, on_resize)

    return window, ctx


if __name__ == "__main__":
    win, context = init_window((400, 300), "Teste de Janela")
    print(f"window.py: Contexto OpenGL inicializado ({context.info['GL_RENDERER']}).")
    context.release()
    glfw.terminate()
