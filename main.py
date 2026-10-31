#!/usr/bin/env python3
"""
Ponto de entrada principal e loop da aplicação Sinucadas (Atividade 02 - Cena 2D Interativa).
Coordena a criação da janela, pipeline gráfico, controles mecânicos e limpeza de recursos.
Oferece suporte aos modos Debug (Hot-Reload via F4) e Release (--release).
"""

import sys
from collections.abc import Callable
from typing import Any

import glfw
import moderngl

from graphics import (
    FELT_COLORS,
    create_scene_balls,
    get_projection_scale,
    render_scene,
    setup_graphics,
)
from window import init_window, register_hot_reload, release_resource, update_time

DEFAULT_WINDOW_SIZE: tuple[int, int] = (800, 600)
ROTATION_SPEED_NORMAL: float = 1.75
ROTATION_SPEED_PRECISION: float = 0.35
POWER_SPEED_NORMAL: float = 0.65
POWER_SPEED_PRECISION: float = 0.15
CUE_POWER_MIN: float = 0.0
CUE_POWER_MAX: float = 1.0


def _print_banner(is_release: bool) -> None:
    """Exibe no terminal o banner de inicialização e o modo de execução."""
    if is_release:
        print("[Sinucadas] 🚀 Release mode enabled (Hot-Reload disabled).")
    else:
        print("[Sinucadas] 🔧 Debug mode enabled (Hot-Reload active via F4 key).")


def _print_controls() -> None:
    """Exibe no terminal o sumário de controles da cena interativa."""
    print("\n[Sinucadas] 🎱 Interactive 2D Billiard Scene initialized!")
    print("Controls:")
    print("  • ← / →: Rotate cue stick and aim line around the cue ball.")
    print("  • Shift + ← / → (or A / D): Precision rotation (5x smoother adjustment).")
    print("  • ↑ / ↓: Pull back / advance cue stick distance.")
    print("  • Shift + ↑ / ↓ (or W / S): Precision distance adjustment (smoother).")
    print("  • C: Change table felt color dynamically in real time.")
    print("  • N: Toggle Day / Night mode (background clear + lighting attenuation).")
    print("  • F4: Reload shaders in real time (Debug mode).")
    print("  • ESC: Exit application.\n")


def _init_cue() -> dict[str, Any]:
    """Inicializa o estado da mira e da distância mecânica do taco de sinuca."""
    return {"angle": 0.0, "power": 0.0, "visible": True}


def _process_cue_controls(cue: dict[str, Any], window: Any, dt: float) -> None:
    """Processa entradas contínuas de rotação mecânica e distância do taco via teclado."""
    is_precision = (
        glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    )
    rotation_speed = ROTATION_SPEED_PRECISION if is_precision else ROTATION_SPEED_NORMAL
    power_speed = POWER_SPEED_PRECISION if is_precision else POWER_SPEED_NORMAL

    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        cue["angle"] += rotation_speed * dt
    elif glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        cue["angle"] += ROTATION_SPEED_PRECISION * dt

    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        cue["angle"] -= rotation_speed * dt
    elif glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        cue["angle"] -= ROTATION_SPEED_PRECISION * dt

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        cue["power"] = min(CUE_POWER_MAX, cue["power"] + power_speed * dt)
    elif glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cue["power"] = min(CUE_POWER_MAX, cue["power"] + POWER_SPEED_PRECISION * dt)

    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        cue["power"] = max(CUE_POWER_MIN, cue["power"] - power_speed * dt)
    elif glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cue["power"] = max(CUE_POWER_MIN, cue["power"] - POWER_SPEED_PRECISION * dt)


def _setup_hot_reload(ctx: moderngl.Context, pipeline: dict[str, Any]) -> None:
    """Registra callback de recarga dinâmica de shaders em tempo de execução."""

    def reload_pipeline() -> None:
        try:
            new_pipeline = setup_graphics(ctx)
            old_pipeline = dict(pipeline)
            pipeline.clear()
            pipeline.update(new_pipeline)
            release_resource(old_pipeline)
            print("[Sinucadas] ✅ Shaders reloaded and pipeline rebuilt successfully!")
        except Exception as exc:
            print(f"[Sinucadas] ❌ Error reloading shaders: {exc}", file=sys.stderr)

    register_hot_reload(reload_pipeline)


def _create_key_callback(
    visual_state: dict[str, Any],
) -> Callable[[Any, int, int, int, int], None]:
    """Cria o callback de teclado tratando comandos discretos (ESC, C, N)."""

    def on_key_event(window_obj: Any, key: int, scancode: int, action: int, mods: int) -> None:
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window_obj, True)
        elif key == glfw.KEY_C:
            visual_state["felt_index"] = (visual_state["felt_index"] + 1) % len(FELT_COLORS)
            print(
                f"[Sinucadas] 🎨 Felt color changed (theme {visual_state['felt_index'] + 1}/{len(FELT_COLORS)})."
            )
        elif key == glfw.KEY_N:
            visual_state["night_mode"] = not visual_state["night_mode"]
            mode_str = (
                "Night (Spotlight)" if visual_state["night_mode"] else "Day (Illuminated Hall)"
            )
            print(f"[Sinucadas] 💡 Toggled to {mode_str} Mode.")

    return on_key_event


def _run_scene_loop(
    window: Any,
    ctx: moderngl.Context,
    pipeline: dict[str, Any],
    balls: list[dict[str, Any]],
    cue: dict[str, Any],
    visual_state: dict[str, Any],
) -> None:
    """Executa o loop contínuo de polling de entrada e renderização da cena 2D."""
    t0 = glfw.get_time()
    while not glfw.window_should_close(window):
        t0, dt = update_time(t0)

        _process_cue_controls(cue, window, dt)
        proj_scale = get_projection_scale(window)

        render_scene(
            ctx=ctx,
            pipeline=pipeline,
            balls=balls,
            proj_scale=proj_scale,
            cue=cue,
            felt_color_index=visual_state["felt_index"],
            night_mode=visual_state["night_mode"],
        )

        glfw.swap_buffers(window)
        glfw.poll_events()


def main() -> None:
    """Executa o loop principal da aplicação Sinucadas."""
    is_release = "--release" in sys.argv
    _print_banner(is_release)

    cue = _init_cue()
    balls = create_scene_balls()
    visual_state = {"felt_index": 0, "night_mode": False}

    key_callback = _create_key_callback(visual_state)
    mode_name = "Release" if is_release else "Debug"
    window, ctx = init_window(
        size=DEFAULT_WINDOW_SIZE,
        title=f"Sinucadas - Interactive 2D Scene [{mode_name}]",
        enable_hot_reload=not is_release,
        user_key_callback=key_callback,
    )

    pipeline = setup_graphics(ctx)
    if not is_release:
        _setup_hot_reload(ctx, pipeline)

    _print_controls()
    _run_scene_loop(window, ctx, pipeline, balls, cue, visual_state)

    release_resource(pipeline, ctx)
    glfw.terminate()


if __name__ == "__main__":
    main()
