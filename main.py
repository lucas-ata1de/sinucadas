#!/usr/bin/env python3
"""
Ponto de entrada principal e loop da aplicação Sinucadas.
Coordena a criação da janela, pipeline gráfico, física/gameplay e limpeza de recursos.
Oferece suporte aos modos Debug (Hot-Reload via F4) e Release (--release).
"""

import sys
from typing import Any

import glfw

from environment import (
    get_projection_scale,
    register_hot_reload,
    release_resource,
    update_time,
)
from gameplay import (
    init_cue,
    init_gameplay,
    process_cue_controls,
    shoot_cue_ball,
    update_gameplay,
)
from graphics import CORES_FELTRO, render_scene, setup_graphics
from window import init_window


def main() -> None:
    """Executa o loop principal da aplicação Sinucadas."""
    is_release = "--release" in sys.argv
    mode_name = "Release" if is_release else "Debug"

    if is_release:
        print("[Sinucadas] 🚀 Modo Release ativado (Hot-Reload desativado).")
    else:
        print("[Sinucadas] 🔧 Modo Debug ativado (Hot-Reload ativo via tecla F4).")

    cue = init_cue()
    felt_color_index = 0
    night_mode = False

    def on_key_event(
        window_obj: Any, key: int, scancode: int, action: int, mods: int
    ) -> None:
        """Trata comandos do teclado para ESC, tacada (ESPAÇO), cor do feltro (C) e modo dia/noite (N)."""
        nonlocal felt_color_index, night_mode
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window_obj, True)
        elif key == glfw.KEY_SPACE:
            if shoot_cue_ball(cue, balls):
                print("[Sinucadas] 💥 Tacada disparada!")
        elif key == glfw.KEY_C:
            felt_color_index = (felt_color_index + 1) % len(CORES_FELTRO)
            print(
                f"[Sinucadas] 🎨 Cor do feltro alterada (tema {felt_color_index + 1}/{len(CORES_FELTRO)})."
            )
        elif key == glfw.KEY_N:
            night_mode = not night_mode
            modo_str = "Noite (Holofote)" if night_mode else "Dia (Salão Iluminado)"
            print(f"[Sinucadas] 💡 Alternado para Modo {modo_str}.")

    window, ctx = init_window(
        size=(800, 600),
        title=f"Sinucadas [{mode_name}]",
        enable_hot_reload=not is_release,
        user_key_callback=on_key_event,
    )

    pipeline = setup_graphics(ctx)

    if not is_release:

        def reload_pipeline() -> None:
            """Recarrega shaders e reconstrói o pipeline gráfico ao disparar hot-reload."""
            try:
                new_pipeline = setup_graphics(ctx)
                old_pipeline = dict(pipeline)
                pipeline.clear()
                pipeline.update(new_pipeline)
                release_resource(old_pipeline)
                print(
                    "[Sinucadas] ✅ Shaders recarregados e pipeline reconstruído com sucesso!"
                )
            except Exception as exc:
                print(
                    f"[Sinucadas] ❌ Erro ao recarregar shaders: {exc}", file=sys.stderr
                )

        register_hot_reload(reload_pipeline)

    balls = init_gameplay()
    t0 = glfw.get_time()

    print("\n[Sinucadas] 🎱 Mesa inicializada com sucesso!")
    print("Controles:")
    print("  • ← / →: Gira a mira do taco ao redor da bola branca.")
    print("  • Shift + ← / → (ou A / D): Mira de precisão (ajuste fino 5x mais suave).")
    print("  • ↑ / ↓: Puxa o taco para trás / dosa a força da tacada.")
    print("  • ESPAÇO: Dispara a tacada na bola branca.")
    print("  • C: Altera a cor do feltro em tempo real.")
    print("  • N: Alterna entre Modo Dia e Modo Noite (atenuação).")
    print("  • F4: Recarrega shaders em tempo real (Modo Debug).")
    print("  • ESC: Fecha a aplicação.\n")

    while not glfw.window_should_close(window):
        t0, dt = update_time(t0)

        process_cue_controls(cue, window, dt)
        balls = update_gameplay(balls, cue, dt)
        proj_scale = get_projection_scale(window)

        render_scene(
            ctx=ctx,
            pipeline=pipeline,
            balls=balls,
            proj_scale=proj_scale,
            cue=cue,
            felt_color_index=felt_color_index,
            night_mode=night_mode,
        )

        glfw.swap_buffers(window)
        glfw.poll_events()

    release_resource(pipeline, ctx)
    glfw.terminate()


if __name__ == "__main__":
    main()
