#!/usr/bin/env python3
"""
Gerenciamento de janelas e callbacks de entrada para o Sinucadas.
Trata a criação da janela GLFW, pooling de eventos, troca de buffers, hot-reload,
controle de viewport, temporização (delta time) e liberação determinística de recursos.
"""

import os
import sys
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from typing import Any

import glfw
import moderngl

from environment import DEFAULT_ICON, apply_icon, configure_cursor, configure_window_hint

_HOT_RELOAD_ENABLED: bool = True
_HOT_RELOAD_KEY: int = getattr(glfw, "KEY_F4", 293)
_HOT_RELOAD_LISTENERS: list[Callable[[], Any]] = []


def glfw_error_callback(code: int, msg: str) -> None:
    """Callback padrão de erros do GLFW direcionado ao stderr."""
    print(f"GLFW [{code}]: {msg}", file=sys.stderr)


def configure_hot_reload(enabled: bool = True, key: int | None = None) -> None:
    """Ativa ou desativa o hot-reload de shaders e opcionalmente configura a tecla de disparo."""
    global _HOT_RELOAD_ENABLED, _HOT_RELOAD_KEY
    _HOT_RELOAD_ENABLED = enabled
    if key is not None:
        _HOT_RELOAD_KEY = key


def register_hot_reload(callback: Callable[[], Any]) -> None:
    """Registra uma função de callback para recompilar shaders e reconstruir o pipeline no hot-reload."""
    if callback not in _HOT_RELOAD_LISTENERS:
        _HOT_RELOAD_LISTENERS.append(callback)


def unregister_hot_reload(callback: Callable[[], Any]) -> None:
    """Remove uma função de callback de hot-reload previamente registrada."""
    with suppress(ValueError):
        _HOT_RELOAD_LISTENERS.remove(callback)


def _trigger_hot_reload() -> bool:
    """Dispara todos os callbacks de hot-reload registrados com tratamento seguro de erros."""
    if not _HOT_RELOAD_ENABLED:
        return False

    print("\n[HOT-RELOAD] 🔄 Triggering shader and pipeline reload...", flush=True)
    if not _HOT_RELOAD_LISTENERS:
        print("[HOT-RELOAD] ℹ️  No hot-reload callback registered.", flush=True)
        return True

    success = True
    for callback in _HOT_RELOAD_LISTENERS:
        try:
            callback()
        except Exception as exc:
            print(
                f"[HOT-RELOAD] ❌ Error reloading pipeline: {exc}", file=sys.stderr, flush=True
            )
            success = False

    if success:
        print("[HOT-RELOAD] ✅ Pipeline and shaders reloaded successfully!\n", flush=True)
    return success


def _check_hot_reload_key(key: int, action: int) -> bool:
    """Verifica se o evento de teclado corresponde à tecla de hot-reload configurada (padrão F4)."""
    if _HOT_RELOAD_ENABLED and action == glfw.PRESS and key == _HOT_RELOAD_KEY:
        _trigger_hot_reload()
        return True
    return False


_ORIGINAL_GLFW_SET_KEY_CALLBACK = glfw.set_key_callback


def set_key_callback(
    window: Any, user_callback: Callable[[Any, int, int, int, int], None] | None = None
) -> None:
    """Define um callback de teclado GLFW na janela interceptando automaticamente a tecla de hot-reload."""

    def _key_handler(win: Any, key: int, scancode: int, action: int, mods: int) -> None:
        if _check_hot_reload_key(key, action):
            return
        if user_callback is not None:
            user_callback(win, key, scancode, action, mods)

    _ORIGINAL_GLFW_SET_KEY_CALLBACK(window, _key_handler)


def _glfw_set_key_callback_hook(
    window: Any, cbfun: Callable[[Any, int, int, int, int], None] | None
) -> Any:
    return set_key_callback(window, cbfun)


glfw.set_key_callback = _glfw_set_key_callback_hook


def _configure_opengl_hints(
    gl_version: tuple[int, int], samples_msaa: int, resizable: bool, app_id: str
) -> None:
    """Configura os hints de versão, perfil, MSAA e identificadores de plataforma no GLFW."""
    major, minor = gl_version
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.SAMPLES, samples_msaa)
    glfw.window_hint(glfw.RESIZABLE, resizable)
    glfw.window_hint(glfw.DEPTH_BITS, 24)
    configure_window_hint(app_id)


def _create_moderngl_context(
    window: Any, depth_test: bool, cull_face: bool, blend: bool
) -> moderngl.Context:
    """Inicializa o contexto ModernGL, ajusta o viewport inicial e habilita os flags de render."""
    ctx = moderngl.create_context()
    ctx.viewport = (0, 0, *glfw.get_framebuffer_size(window))

    if depth_test:
        ctx.enable(moderngl.DEPTH_TEST)
    if cull_face:
        ctx.enable(moderngl.CULL_FACE)
    if blend:
        ctx.enable(moderngl.BLEND)

    return ctx


def window_setup(
    size: tuple[int, int] = (800, 600),
    title: str = "ModernGL",
    resizable: bool = True,
    vsync: bool = True,
    gl_version: tuple[int, int] = (4, 0),
    samples_msaa: int = 4,
    app_id: str = "moderngl",
    icon_path: Path | str | None = DEFAULT_ICON,
    enable_hot_reload: bool = True,
    hot_reload_key: int | None = None,
    depth_test: bool = False,
    cull_face: bool = False,
    blend: bool = False,
) -> tuple[Any, moderngl.Context]:
    """Inicializa o GLFW, define hints de plataforma, cria janela e contexto ModernGL e aplica o ícone."""
    configure_hot_reload(enabled=enable_hot_reload, key=hot_reload_key)
    configure_cursor()
    glfw.set_error_callback(glfw_error_callback)

    if not glfw.init():
        sys.exit("FAILURE: Unable to initialize GLFW")

    _configure_opengl_hints(gl_version, samples_msaa, resizable, app_id)

    window = glfw.create_window(*size, title, None, None)
    if not window:
        glfw.terminate()
        sys.exit("FAILURE: Unable to create GLFW window")

    glfw.make_context_current(window)
    glfw.swap_interval(1 if vsync else 0)
    apply_icon(window, icon_path)
    set_key_callback(window, None)

    ctx = _create_moderngl_context(window, depth_test, cull_face, blend)
    return window, ctx


def _default_key_callback(window: Any, key: int, scancode: int, action: int, mods: int) -> None:
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

    active_callback = user_key_callback or _default_key_callback
    glfw.set_key_callback(window, active_callback)
    glfw.set_framebuffer_size_callback(window, on_resize)

    return window, ctx


def adjust_viewport(ctx: moderngl.Context, size: tuple[int, int]) -> bool:
    """Atualiza o viewport do ModernGL apenas se largura e altura forem positivas (evita crash ao minimizar)."""
    width, height = size
    if width > 0 and height > 0:
        ctx.viewport = (0, 0, width, height)
        return True
    return False


def update_time(before: float, dt_max: float | None = None) -> tuple[float, float]:
    """Calcula o tempo atual e delta time, com clamp opcional em dt_max para estabilidade da física."""
    now = glfw.get_time()
    dt = now - before
    if dt_max is not None and dt_max > 0 and dt > dt_max:
        dt = dt_max
    return now, dt


def release_resource(*resources: Any) -> None:
    """Libera recursos ModernGL com segurança, desempacotando recursivamente listas, tuplas, sets e dicts."""
    for res in resources:
        if res is None:
            continue
        if isinstance(res, (list, tuple, set)):
            release_resource(*res)
        elif isinstance(res, dict):
            release_resource(*res.values())
        elif hasattr(res, "release"):
            with suppress(Exception):
                res.release()


def main() -> None:
    """Executa a suíte de testes unitários de temporização, viewport e janelas do Sinucadas."""
    # 1. Test delta time and dt_max clamp
    t_base = glfw.get_time() if glfw.init() else 100.0
    now, dt = update_time(t_base)
    assert dt >= 0.0, "Delta time must be non-negative"
    _, dt_clamped = update_time(now - 1.0, dt_max=0.05)
    assert dt_clamped == 0.05, f"dt_max must clamp value to 0.05, got {dt_clamped}"

    # 2. Test viewport adjustment with valid and degenerate dimensions
    class _MockContext:
        viewport = (0, 0, 0, 0)

    mock_ctx = _MockContext()
    assert adjust_viewport(mock_ctx, (800, 600)) is True  # type: ignore[arg-type]
    assert mock_ctx.viewport == (0, 0, 800, 600)
    assert adjust_viewport(mock_ctx, (0, 0)) is False  # type: ignore[arg-type]
    assert adjust_viewport(mock_ctx, (-100, 400)) is False  # type: ignore[arg-type]

    # 3. Test composite resource release
    released_count = 0

    class _MockResource:
        def release(self) -> None:
            nonlocal released_count
            released_count += 1

    r1, r2, r3, r4 = _MockResource(), _MockResource(), _MockResource(), _MockResource()
    release_resource(None, r1, [r2, (r3, {"nested": r4})])
    assert released_count == 4, f"Expected 4 resources released, got {released_count}"

    # 4. Test hot-reload observer subsystem
    reload_triggered = False

    def _sample_callback() -> None:
        nonlocal reload_triggered
        reload_triggered = True

    register_hot_reload(_sample_callback)
    assert _sample_callback in _HOT_RELOAD_LISTENERS
    _trigger_hot_reload()
    assert reload_triggered is True, "Hot-reload callback was not executed"
    unregister_hot_reload(_sample_callback)
    assert _sample_callback not in _HOT_RELOAD_LISTENERS

    # 5. Test window creation and ModernGL context (invisible/headless-safe)
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        print("window.py: unit tests (timing, viewport, release, hot-reload) passed (GUI skipped in headless).")
    else:
        glfw.window_hint(glfw.VISIBLE, False)
        win, context = window_setup((400, 300), "Window Test")
        renderer = context.info["GL_RENDERER"]
        print(f"window.py: unit tests and ModernGL context verified successfully ({renderer}).")
        release_resource(context)
        glfw.terminate()


if __name__ == "__main__":
    main()
