#!/usr/bin/env python3
"""
Ponto de entrada principal e loop da aplicação Sinucadas.
Coordena a criação da janela, inicialização gráfica, física/gameplay e limpeza de recursos.
Oferece suporte aos modos Debug (Hot-Reload via F4) e Release (--release).
"""

import sys

import glfw

from environment import register_hot_reload, release_resource, update_time
from gameplay import init_gameplay, update_gameplay
from graphics import render_frame, setup_graphics
from window import init_window


def main() -> None:
    """Executa o loop principal da aplicação Sinucadas."""
    is_release = "--release" in sys.argv
    mode_name = "Release" if is_release else "Debug"

    if is_release:
        print("[Sinucadas] 🚀 Modo Release ativado (Hot-Reload desativado).")
    else:
        print("[Sinucadas] 🔧 Modo Debug ativado (Hot-Reload ativo via tecla F4).")

    window, ctx = init_window(
        size=(800, 600),
        title=f"Sinucadas [{mode_name}]",
        enable_hot_reload=not is_release,
    )
    prog, vbo, ebo, vao = setup_graphics(ctx)
    pipeline = {"prog": prog, "vbo": vbo, "ebo": ebo, "vao": vao}

    if not is_release:
        def reload_pipeline() -> None:
            """Recarrega shaders e reconstrói o pipeline gráfico ao disparar hot-reload."""
            try:
                new_prog, new_vbo, new_ebo, new_vao = setup_graphics(ctx)
                old_vao, old_vbo, old_ebo, old_prog = (
                    pipeline["vao"],
                    pipeline["vbo"],
                    pipeline["ebo"],
                    pipeline["prog"],
                )
                pipeline["prog"] = new_prog
                pipeline["vbo"] = new_vbo
                pipeline["ebo"] = new_ebo
                pipeline["vao"] = new_vao
                release_resource(old_vao, old_vbo, old_ebo, old_prog)
                print("[Sinucadas] ✅ Shaders recarregados e pipeline reconstruído com sucesso!")
            except Exception as exc:
                print(f"[Sinucadas] ❌ Erro ao recarregar shaders: {exc}", file=sys.stderr)

        register_hot_reload(reload_pipeline)

    y_pos = init_gameplay()
    t0 = glfw.get_time()

    while not glfw.window_should_close(window):
        t0, dt = update_time(t0)

        y_pos = update_gameplay(y_pos, dt)
        render_frame(ctx, pipeline["prog"], pipeline["vao"], y_pos)

        glfw.swap_buffers(window)
        glfw.poll_events()

    release_resource(pipeline, ctx)
    glfw.terminate()


if __name__ == "__main__":
    main()
