#!/usr/bin/env python3
"""
Sinucadas — Jogo 2D Animado Multiplayer de Sinuca (Atividade 03 - Computação Gráfica UFABC)
===========================================================================================
Jogo 2D multiplayer (Jogador 1 vs Jogador 2) em tempo real sob perfil estrito OpenGL 4.0 Core,
com alternância de turnos, sistema de pontuação de sinuca (valor nominal das bolas e +4 pts
para o adversário em faltas), taco com cores exclusivas por jogador (P1 Azul Safira / P2 Vermelho Rubi),
física elástica por sub-stepping (anti-tunelamento), raycast analítico de mira (Ghost Ball),
animações autônomas periódicas e placar no título e na cena.

Instruções de Execução:
  • Modo Debug (Hot-Reload F4 ativo):  python3 main.py      (ou `make run`)
  • Modo Release (Otimizado):          python3 main.py --release (ou `make release`)
  • Suíte de Testes Unitários:         make test

Lista Completa de Teclas e Controles:
  • SETAS ESQUERDA / DIREITA: Gira a mira do taco ao redor da bola branca (modo ágil).
  • SHIFT + ESQUERDA / DIREITA (ou A / D): Mira de alta precisão (5x mais suave).
  • SETAS CIMA / BAIXO: Puxa o taco e ajusta a potência da tacada (modo ágil).
  • SHIFT + CIMA / BAIXO (ou W / S): Ajuste fino de potência da tacada.
  • ESPAÇO: Dispara a tacada do jogador da vez (e inicia a partida no estado START).
  • P: Pausa ou retoma a partida (congela a física sem acumular Δt).
  • R: Reinicia a partida completa (turnos, bolas, placar e vidas) sem fechar a janela.
  • V: Alterna V-Sync ligado/desligado em tempo real (`glfw.swap_interval`).
  • C: Alterna ciclicamente a cor do feltro da mesa (Verde, Azul, Vermelho, Grafite).
  • N: Alterna entre o modo Dia (salão iluminado) e Noite (holofote com atenuação).
  • F4: Recarrega os shaders GLSL em tempo real sem reiniciar (modo Debug).
  • ESC: Encerra a aplicação e libera determinísticamente os recursos de GPU.
"""

import sys
from collections.abc import Callable
from typing import Any

import glfw
import moderngl

from gameplay import (
    STATE_GAME_OVER,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_START,
    STATE_VICTORY,
    init_cue,
    init_game_state,
    init_gameplay,
    process_cue_controls,
    reset_match,
    shoot_cue_ball,
    update_gameplay,
)
from graphics import FELT_COLORS, get_projection_scale, render_scene, setup_graphics
from window import init_window, register_hot_reload, release_resource, update_time

MAX_DT = 0.05
PLAYER_LABELS = ("P1 Azul", "P2 Vermelho")
DEFAULT_WINDOW_SIZE: tuple[int, int] = (960, 680)
FPS_UPDATE_INTERVAL: float = 0.25


def _print_banner(is_release: bool) -> None:
    """Exibe no terminal o banner de inicialização e o modo de execução."""
    if is_release:
        print("[Sinucadas] 🚀 Release mode enabled (Hot-Reload disabled).")
    else:
        print("[Sinucadas] 🔧 Debug mode enabled (Hot-Reload active via F4 key).")


def _print_controls() -> None:
    """Exibe no terminal o sumário completo de controles e regras multiplayer."""
    print("\n[Sinucadas] 🎱 2D Multiplayer Animated Billiards (P1 Blue vs P2 Red) initialized!")
    print("Controls:")
    print("  • ← / →: Rotate cue aim around the cue ball.")
    print("  • Shift + ← / → (or A / D): Precision aiming (5x smoother adjustment).")
    print("  • ↑ / ↓: Pull cue back / adjust shot power.")
    print("  • Shift + ↑ / ↓ (or W / S): Precision power adjustment.")
    print("  • SPACE: Shoot the cue ball for the active player.")
    print("  • P: Pause / resume game (freezes physics without Δt jump).")
    print("  • R: Restart match (resets turns, balls, scores, and lives).")
    print("  • V: Toggle V-Sync ON/OFF (displays real-time FPS in window title).")
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
    cue: dict[str, Any],
    balls: list[dict[str, Any]],
    visual_state: dict[str, Any],
    game_state: dict[str, Any],
) -> Callable[[Any, int, int, int, int], None]:
    """Cria o callback de teclado tratando comandos discretos (ESC, ESPAÇO, P, R, V, C, N)."""

    def on_key_event(window_obj: Any, key: int, scancode: int, action: int, mods: int) -> None:
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window_obj, True)
        elif key == glfw.KEY_SPACE:
            cur_p = int(game_state.get("current_player", 1))
            if shoot_cue_ball(cue, balls, game_state):
                print(
                    f"[Sinucadas] 💥 Tacada #{game_state['shots']} disparada pelo Jogador {cur_p} ({PLAYER_LABELS[cur_p - 1]})!"
                )
        elif key == glfw.KEY_P:
            if game_state["state"] == STATE_PLAYING:
                game_state["state"] = STATE_PAUSED
                print("[Sinucadas] ⏸️  Jogo pausado.")
            elif game_state["state"] == STATE_PAUSED:
                game_state["state"] = STATE_PLAYING
                print("[Sinucadas] ▶️  Jogo retomado.")
        elif key == glfw.KEY_R:
            reset_match(balls, cue, game_state)
            print("[Sinucadas] 🔄 Partida multiplayer reiniciada!")
        elif key == glfw.KEY_V:
            visual_state["vsync"] = not visual_state["vsync"]
            glfw.swap_interval(1 if visual_state["vsync"] else 0)
            vsync_str = "ON" if visual_state["vsync"] else "OFF"
            print(f"[Sinucadas] 🖥️  V-Sync alterado para {vsync_str}.")
        elif key == glfw.KEY_C:
            visual_state["felt_index"] = (visual_state["felt_index"] + 1) % len(FELT_COLORS)
            print(
                f"[Sinucadas] 🎨 Cor do feltro alterada (tema {visual_state['felt_index'] + 1}/{len(FELT_COLORS)})."
            )
        elif key == glfw.KEY_N:
            visual_state["night_mode"] = not visual_state["night_mode"]
            mode_str = (
                "Noite (Holofote)" if visual_state["night_mode"] else "Dia (Salão Iluminado)"
            )
            print(f"[Sinucadas] 💡 Modo alterado para {mode_str}.")

    return on_key_event


def _format_window_title(
    game_state: dict[str, Any],
    vsync: bool,
    fps: float,
) -> str:
    """Formata o título da janela exibindo turno ativo, pontuação P1 vs P2, estado, V-Sync e FPS."""
    cur_p = int(game_state.get("current_player", 1))
    turn_label = PLAYER_LABELS[(cur_p - 1) % 2]
    scores = game_state.get("scores", [0, 0])
    pocketed = game_state.get("balls_pocketed", [0, 0])

    state = game_state["state"]
    if state in (STATE_VICTORY, STATE_GAME_OVER):
        winner = int(game_state.get("winner", 1))
        win_label = PLAYER_LABELS[(winner - 1) % 2]
        status_str = f"VENCEDOR: {win_label}! (R reinicia)"
    elif state == STATE_PAUSED:
        status_str = f"PAUSADO — Vez: {turn_label} (P continua)"
    elif state == STATE_START:
        status_str = f"INÍCIO — Vez: {turn_label}"
    else:
        status_str = f"Vez: {turn_label}"

    vsync_str = "ON" if vsync else "OFF"
    return (
        f"Sinucadas | {status_str} | "
        f"Placar: P1 {scores[0]} pts ({pocketed[0]}) x P2 {scores[1]} pts ({pocketed[1]}) | "
        f"VSync: {vsync_str} | {fps:5.1f} FPS"
    )


def _run_game_loop(
    window: Any,
    ctx: moderngl.Context,
    pipeline: dict[str, Any],
    balls: list[dict[str, Any]],
    cue: dict[str, Any],
    visual_state: dict[str, Any],
    game_state: dict[str, Any],
) -> None:
    """Executa o loop contínuo de simulação física (Δt limitado), entrada e renderização."""
    last_time = glfw.get_time()
    fps_timer = last_time
    frame_count = 0
    anim_time = 0.0

    reset_match(balls, cue, game_state)

    while not glfw.window_should_close(window):
        now, dt = update_time(last_time, dt_max=MAX_DT)
        last_time = now

        if game_state["state"] != STATE_PAUSED:
            anim_time += dt
            process_cue_controls(cue, window, dt, balls, game_state)
            update_gameplay(balls, cue, dt, game_state=game_state)

        proj_scale = get_projection_scale(window)

        render_scene(
            ctx=ctx,
            pipeline=pipeline,
            balls=balls,
            proj_scale=proj_scale,
            cue=cue,
            felt_color_index=visual_state["felt_index"],
            night_mode=visual_state["night_mode"],
            game_state=game_state,
            anim_time=anim_time,
        )

        glfw.swap_buffers(window)
        glfw.poll_events()

        frame_count += 1
        if now - fps_timer >= FPS_UPDATE_INTERVAL:
            fps = frame_count / (now - fps_timer)
            glfw.set_window_title(
                window,
                _format_window_title(game_state, visual_state["vsync"], fps),
            )
            frame_count = 0
            fps_timer = now


def main() -> None:
    """Executa o loop principal da aplicação Sinucadas (Atividade 03)."""
    is_release = "--release" in sys.argv
    _print_banner(is_release)

    cue = init_cue()
    balls = init_gameplay()
    game_state = init_game_state()
    visual_state = {"felt_index": 0, "night_mode": False, "vsync": True}

    key_callback = _create_key_callback(cue, balls, visual_state, game_state)
    mode_name = "Release" if is_release else "Debug"
    window, ctx = init_window(
        size=DEFAULT_WINDOW_SIZE,
        title=f"Sinucadas [{mode_name}]",
        enable_hot_reload=not is_release,
        user_key_callback=key_callback,
    )

    pipeline = setup_graphics(ctx)
    if not is_release:
        _setup_hot_reload(ctx, pipeline)

    _print_controls()
    _run_game_loop(window, ctx, pipeline, balls, cue, visual_state, game_state)

    release_resource(pipeline, ctx)
    glfw.terminate()


if __name__ == "__main__":
    main()
