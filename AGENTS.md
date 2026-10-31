# 🧠 AGENTS.md — Governança Técnica (Sinucadas — Atividade 03)

Diretrizes de arquitetura, cinemática analítica e contratos de qualidade para o jogo Sinucadas (Atividade 03 - Jogo 2D Animado Multiplayer).

---

## 1. Identidade e Escopo do Projeto

O **Sinucadas (Atividade 03)** é um jogo 2D multiplayer (P1 Azul Safira vs P2 Vermelho Rubi) sob **OpenGL 4.0 Core Profile** (`#version 400 core`), implementando física elástica com sub-stepping adaptativo (anti-tunelamento), raycast analítico de mira (Ghost Ball), alternância de turnos, placar oficial de sinuca e renderização de HUD em cena.

---

## 2. Invariantes Arquiteturais e Cinemáticos

### Regra 1: Correlação Paramétrica de Domínio

- **Regra:** Todas as grandezas físicas, de mesa e de interface devem ser matematicamente derivadas das dimensões fundamentais:
    - `TABLE_BOUNDS = (TABLE_WIDTH, TABLE_HEIGHT)`
    - `BAULK_LINE_X = -TABLE_WIDTH / 2.0`
    - `CUE_BALL_INITIAL_POS = (-TABLE_WIDTH / 2.0, 0.0)`
    - `RACK_ORIGIN_X = TABLE_WIDTH / 3.0`
    - `RACK_DX_FACTOR = sqrt(3.0) / 2.0`
    - `HUD_BOTTOM_Y = -HUD_TOP_Y`
    - `SCENE_HALF_WIDTH = TABLE_WIDTH + CUSHION_THICKNESS`
    - `SCENE_HALF_HEIGHT = abs(HUD_TOP_Y) + HUD_BADGE_RADIUS + HUD_PADDING`
- **Evite:** Números literais soltos no código ou pré-cálculos arbitrários.

### Regra 2: Isolamento em Múltiplos VBOs

- **Regra:** VBOs estáticos (área de feltro, moldura de madeira, linhas da mesa, anel de mira e quadriláteros do HUD) devem residir imutáveis na VRAM. O taco dinâmico e elementos variáveis utilizam buffers próprios sem contaminação dos buffers perenes.
- **Evite:** Alocações recorrentes de GPU por quadro no loop de gameplay.

### Regra 3: Física Determinística e Sub-stepping

- **Regra:** A resolução de cinemática deve subdividir passos de tempo ($\Delta t$) em fatias seguras limitadas pelo raio da menor esfera, impedindo tunelamento através das tabelas ou entre bolas.
- **Evite:** Integração de Euler explícita com passo largo desprovida de verificação contínua de colisão.

### Regra 4: Proibição Estrita de Comentários no Código (Zero Inline Comments)

- **Regra:** O código Python do jogo é 100% autoexplicativo e não deve conter comentários (`# ...`). Toda a explicação arquitetural, modelagem física e detalhes de regras pertencem exclusivamente ao `README.md` e ao `AGENTS.md`.
- **Evite:** Inserir qualquer comentário explicativo inline no código.
- **Use:** Clean Code, tipagem estática rigorosa e docstrings contratuais concisas.

### Regra 5: Padrão Idiomático Estrito (Código em Inglês, Docstrings em Português)

- **Regra:** Todas as entidades de código (classes, funções, variáveis, constantes, uniforms e atributos) devem ser expressas estritamente em inglês. Docstrings contratuais e arquivos `.md` devem ser expressos em português formal.
- **Evite:** Identificadores em português (`turno_jogador`, `posicao_branca`) ou docstrings misturando idiomas.
- **Use:** API e identificadores em inglês (`active_player`, `cue_ball_pos`), acompanhados de docstrings contratuais em português.

---

## 3. Comandos de Validação e Execução

```bash
make run           # Executa o jogo em modo Debug (Hot-Reload F4 ativo)
make release       # Executa o jogo em modo Release otimizado
make test          # Executa testes unitários de regras, física elástica e HUD
make check         # Validação estática: Pyright (0 erros) e Ruff (0 alertas)
make clean         # Remoção de caches locais
```
