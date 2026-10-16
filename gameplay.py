#!/usr/bin/env python3
"""
Lógica de jogo e atualização de estado para o Sinucadas.
Gerencia posições de objetos, parâmetros de velocidade e progressão temporal de estado.
"""

SPEED = 0.5
START_Y, END_Y = -0.9, 0.9


def init_gameplay() -> float:
    """Inicializa e retorna a posição vertical inicial do elemento."""
    return START_Y


def update_gameplay(
    y_pos: float,
    dt: float,
    speed: float = SPEED,
    start_y: float = START_Y,
    end_y: float = END_Y,
) -> float:
    """Atualiza a posição vertical baseada no delta time e reinicia ao atingir o limite."""
    y_pos += speed * dt
    if y_pos > end_y:
        y_pos = start_y
    return y_pos


if __name__ == "__main__":
    pos = init_gameplay()
    pos = update_gameplay(pos, dt=0.1)
    assert pos > START_Y
    assert update_gameplay(END_Y + 0.1, dt=0.1) == START_Y
    print(f"gameplay.py: testes de atualização de estado passaram com sucesso (pos={pos:.2f}).")
