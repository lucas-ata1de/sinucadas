# Sinucadas — Jogo 2D Animado (Atividade 03)

Jogo 2D interativo e multiplayer (P1 vs P2) de sinuca desenvolvido em Python para a **Atividade 03** de Computação Gráfica (UFABC), utilizando **ModernGL**, **GLFW**, **NumPy** e **PyGLM** sobre o perfil estrito **OpenGL 4.0 Core Profile**.

---

## 🎮 Como Jogar e Controles

O jogo conta com modo **Multiplayer Local (Jogador 1 Azul vs Jogador 2 Vermelho)** em turnos alternados, pontuação oficial de sinuca no título da janela e no HUD geométrico, raycast analítico de mira (Ghost Ball), dosagem de força, máquina de estados (Início, Jogo, Pausa, Vitória e Derrota) e controle de V-Sync.

| Tecla | Ação | Descrição |
| :--- | :--- | :--- |
| `←` / `→` | **Girar Mira (Ágil)** | Rotaciona o taco de sinuca e a linha guia tracejada ao redor da bola branca em velocidade normal (1.75 rad/s). |
| `Shift + ← / →` | **Mira de Precisão** | Modo de ajuste fino (0.35 rad/s, 5x mais suave) para alinhamentos milimétricos em bolas ou caçapas distantes. |
| `A` / `D` | **Mira Alternativa** | Micro-ajustes de mira para correções minuciosas de ângulo. |
| `↑` / `↓` | **Dosar Força (Ágil)** | Puxa o taco para trás aumentando a força da tacada ou diminui a força (velocidade normal). |
| `Shift + ↑ / ↓` | **Força com Precisão** | Ajuste fino e suave da dosagem de força da tacada. |
| `W` / `S` | **Força Alternativa** | Micro-ajustes de dosagem de força utilizando a mão esquerda. |
| `ESPAÇO` | **Tacada / Iniciar** | Aplica o impulso na bola branca na direção e intensidade configuradas (e inicia a partida a partir de `START`). |
| `P` | **Pausar / Retomar** | Congela ou retoma a simulação física sem acumular o tempo pausado em $\Delta t$. |
| `R` | **Reiniciar Partida** | Reinicia o estado completo da partida (16 bolas, 3 vidas, turnos e placar zerado) sem fechar a janela. |
| `V` | **Alternar V-Sync** | Liga ou desliga o V-Sync (`glfw.swap_interval`) para demonstrar independência de FPS. |
| `C` | **Cor do Feltro** | Alterna ciclicamente a cor da mesa em tempo real (Verde, Azul, Vermelho e Grafite). |
| `N` | **Dia / Noite** | Alterna entre o modo Dia (salão iluminado) e Noite (holofote focado na mesa com atenuação de luz). |
| `F4` | **Hot-Reload** | Recarrega shaders GLSL em tempo real sem reiniciar a aplicação (disponível no modo Debug). |
| `ESC` | **Sair** | Encerra a aplicação e libera com segurança todos os recursos gráficos alocados na GPU. |

---

## 🎱 Mecânicas Multiplayer, Pontuação e Modelo Físico

1. **Multiplayer em Turnos & Cores de Taco por Jogador**:
   - **Jogador 1 (Azul Safira)** e **Jogador 2 (Vermelho Rubi)** possuem cores exclusivas tanto no taco quanto na linha guia tracejada e na Ghost Ball, moduladas dinamicamente via `u_color` sem reescrever VBOs.
   - Se o jogador da vez encaçapar ao menos uma bola válida sem cometer falta, **continua jogando**; caso não encaçape nenhuma bola ou cometa falta, **o turno passa para o adversário** assim que todas as bolas param.
2. **Sistema de Pontuação de Sinuca & Placar no Título**:
   - Cada bola numerada vale sua pontuação nominal (**1 a 15 pontos**).
   - **Faltas** (encaçapar a bola branca ou encaçapar a Bola 8 antes de limpar a mesa) concedem **+4 pontos de penalidade** ao adversário, descontam 1 vida coletiva da mesa e passam a vez.
   - O título da janela exibe em tempo real o turno ativo, os pontos e bolas encaçapadas de cada jogador (`Placar: P1 X pts (N) x P2 Y pts (M)`), o estado da partida, V-Sync e FPS.
3. **Sub-stepping Temporal Anti-Tunelamento**: O intervalo $\Delta t$ (limitado a `MAX_DT = 0.05s`) é subdividido dinamicamente em 4 a 16 sub-passos por quadro, garantindo que nenhuma bola percorra mais que $0.45 R$ por sub-passo e eliminando tunelamento em altas velocidades.
4. **Raycast Analítico de Mira & Ghost Ball**: Calcula em tempo real a interseção da trajetória da bola branca com a bola ou tabela mais próxima, desenhando uma **Ghost Ball pulsante** (`moderngl.LINE_LOOP`) no ponto exato do impacto e a linha de deflexão da bola alvo (`moderngl.LINES`).
5. **HUD Geométrico Multiplayer na Cena**: Placar superior dividido entre **P1 (esquerda)** e **P2 (direita)** com emblema colorido de cada jogador, anel pulsante indicando de quem é a vez, slots das bolas encaçapadas por cada jogador (`TRIANGLE_FAN` / `LINE_LOOP`), medidor de potência de 10 níveis (`TRIANGLES`) e 3 indicadores de vida no topo direito.
6. **Reaproveitamento Estrito de VBOs Estáticos**: Todos os 7 VBOs são alocados uma única vez na inicialização (`setup_graphics`), e todas as transformações (recuo do taco, comprimento da mira e cor do taco por jogador) são feitas via variáveis `uniform` no shader.

---

## 📁 Estrutura do Projeto

- `main.py`: Ponto de entrada, loop principal com controle de $\Delta t$, placar multiplayer no título da janela, FPS, V-Sync e callbacks de teclado.
- `graphics.py`: Compilação de shaders, VBOs/EBOs/VAOs estáticos de 5 primitivas (`TRIANGLES`, `TRIANGLE_FAN`, `LINE_STRIP`, `LINE_LOOP`, `LINES`), cores de taco por jogador e renderização do HUD multiplayer.
- `gameplay.py`: Máquina de estados, regras de turnos (P1 vs P2), pontuação de sinuca (+4 pts por falta), sub-stepping temporal e controle de mira/força.
- `physics.py`: Motor de física 2D (colisões elásticas bola-bola, rebote nas tabelas com abertura nas caçapas, captura radial e raycast analítico da Ghost Ball).
- `window.py`: Inicialização da janela GLFW, callbacks de teclado, hot-reload (`F4`) e redimensionamento de viewport.
- `environment.py`: Utilitários de plataforma (XCURSOR e ícones no Wayland/X11).
- `shaders/shader.vert` & `shaders/shader.frag`: Shaders GLSL `#version 400 core`.
- `Makefile`: Orquestrador de execução, testes unitários e análise estática.

---

## 🛠️ Setup do Ambiente Virtual

Para preparar e isolar o ambiente Python em qualquer sistema operacional, utilize o gerenciador de sua escolha (`conda`, `venv` nativo ou `uv`):

### Windows

#### Conda
```pwsh
conda create -n cgcourse python=3.11
conda activate cgcourse
pip install glfw moderngl numpy pyglm pillow
```

#### venv
```pwsh
python3.11 -m venv .venv
.venv\Scripts\activate
pip install glfw moderngl numpy pyglm pillow
```

#### uv
```pwsh
uv venv --python 3.11
.venv\Scripts\activate
uv pip install glfw moderngl numpy pyglm pillow
```

### Linux / BSD

#### Conda
```sh
conda create -n cgcourse python=3.11
conda activate cgcourse
pip install glfw moderngl numpy pyglm pillow
```

#### venv
```sh
python3.11 -m venv .venv
source .venv/bin/activate
pip install glfw moderngl numpy pyglm pillow
```

#### uv
```sh
uv venv --python 3.11
source .venv/bin/activate
uv pip install glfw moderngl numpy pyglm pillow
```

---

## 🚀 Como Executar

```bash
make run        # Modo Debug (Hot-Reload F4 ativo)
make release    # Modo Release (--release)
make test       # Executa suíte de testes unitários de todos os módulos
make check      # Executa verificação estática (Ruff + Pyright)
make clean      # Remove caches temporários (__pycache__, *.pyc, .ruff_cache)
make purge      # Remove ambientes virtuais (.venv), caches e arquivos temporários
```

---

## 🧼 Diretrizes de Clean Code & Boas Práticas

Todos os módulos do jogo atendem às boas práticas de engenharia e Clean Code:

1. **Proibição Estrita de Números Mágicos (`Magic Numbers`):** Valores literais arbitrários no fluxo lógico foram completamente substituídos por constantes semânticas explícitas no topo de cada módulo (`PROJECTION_MARGIN = 0.96`, `BALL_RADIUS = 0.032`, `TABLE_BOUNDS = (0.90, 0.45)`, `CUSHION_RESTITUTION = 0.85`, `BALL_RESTITUTION = 0.96`, `ROLLING_FRICTION_BASE = 0.985`, `REFERENCE_FPS = 60.0`, `MAX_DT = 0.05`, etc.).
2. **Padronização de Proporções e Margens:** A projeção isotrópica adota `PROJECTION_MARGIN = 0.96`, assegurando proporção 1:1 rigorosa sem distorção das esferas e acomodando o HUD superior/inferior.
3. **Nomenclatura Descritiva e Tipagem Estrita:**
   - Funções e variáveis em `snake_case`.
   - Classes em `PascalCase`.
   - Constantes globais em `UPPER_SNAKE_CASE`.
   - Shaders com prefixos padronizados (`v_position`, `v_color`, `u_offset`, `u_scale`, `u_angle`, `u_color`, `u_proj`, `u_attenuation`, `v2f_color`, `frag_color`).
4. **Modularidade e Separação de Responsabilidades:** Separação estrita entre física analítica (`physics.py`), máquina de estados e regras (`gameplay.py`), buffers e pipeline GPU (`graphics.py`), ciclo de vida GLFW (`window.py`) e plataforma (`environment.py`).
