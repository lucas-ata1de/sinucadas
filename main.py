#!/usr/bin/env python3
"""
Ponto de entrada principal e loop da aplicação Sinucadas.
Coordena a criação da janela, pipeline gráfico, física/gameplay e limpeza de recursos.
Oferece suporte aos modos Debug (Hot-Reload via F4) e Release (--release).
"""

import sys
from collections.abc import Callable
from typing import Any

import glfw
import moderngl

from gameplay import (
    init_cue,
    init_gameplay,
    process_cue_controls,
    shoot_cue_ball,
    update_gameplay,
)
from graphics import FELT_COLORS, get_projection_scale, render_scene, setup_graphics
from window import init_window, register_hot_reload, release_resource, update_time


def _print_banner(is_release: bool) -> None:
    """Exibe no terminal o banner de inicialização e o modo de execução."""
    if is_release:
        print("[Sinucadas] 🚀 Release mode enabled (Hot-Reload disabled).")
    else:
        print("[Sinucadas] 🔧 Debug mode enabled (Hot-Reload active via F4 key).")


def _print_controls() -> None:
    """Exibe no terminal o sumário de controles do jogo."""
    print("\n[Sinucadas] 🎱 Table initialized successfully!")
    print("Controls:")
    print("  • ← / →: Rotate cue aim around the cue ball.")
    print("  • Shift + ← / → (or A / D): Precision aiming (5x smoother adjustment).")
    print("  • ↑ / ↓: Pull cue back / adjust shot power.")
    print("  • SPACE: Shoot the cue ball.")
    print("  • C: Change table felt color in real time.")
    print("  • N: Toggle between Day and Night mode (attenuation).")
    print("  • F4: Reload shaders in real time (Debug mode).")
    print("  • ESC: Exit application.\n")


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
    cue: dict[str, Any], balls: list[dict[str, Any]], visual_state: dict[str, Any]
) -> Callable[[Any, int, int, int, int], None]:
    """Cria o callback de teclado tratando comandos discretos (ESC, ESPAÇO, C, N)."""

    def on_key_event(window_obj: Any, key: int, scancode: int, action: int, mods: int) -> None:
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window_obj, True)
        elif key == glfw.KEY_SPACE:
            if shoot_cue_ball(cue, balls):
                print("[Sinucadas] 💥 Shot fired!")
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


def _run_game_loop(
    window: Any,
    ctx: moderngl.Context,
    pipeline: dict[str, Any],
    balls: list[dict[str, Any]],
    cue: dict[str, Any],
    visual_state: dict[str, Any],
) -> None:
    """Executa o loop contínuo de simulação física, polling de entrada e renderização gráfica."""
    t0 = glfw.get_time()
    while not glfw.window_should_close(window):
        t0, dt = update_time(t0)

        process_cue_controls(cue, window, dt)
        update_gameplay(balls, cue, dt)
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

    cue = init_cue()
    balls = init_gameplay()
    visual_state = {"felt_index": 0, "night_mode": False}

    key_callback = _create_key_callback(cue, balls, visual_state)
    mode_name = "Release" if is_release else "Debug"
    window, ctx = init_window(
        size=(800, 600),
        title=f"Sinucadas [{mode_name}]",
        enable_hot_reload=not is_release,
        user_key_callback=key_callback,
    )

    pipeline = setup_graphics(ctx)
    if not is_release:
        _setup_hot_reload(ctx, pipeline)

    _print_controls()
    _run_game_loop(window, ctx, pipeline, balls, cue, visual_state)

    release_resource(pipeline, ctx)
    glfw.terminate()


if __name__ == "__main__":
    main()
