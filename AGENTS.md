# 🧠 AGENTS.md — Governança Técnica (Sinucadas — Atividade 02)

Diretrizes de arquitetura, invariantes geométricas e contratos de qualidade para o projeto Sinucadas (Cena 2D Interativa).

---

## 1. Identidade e Escopo do Projeto

O **Sinucadas (Atividade 02)** é uma aplicação gráfica 2D interativa desenvolvida sob o perfil estrito **OpenGL 4.0 Core** (`#version 400 core`), implementando a renderização de uma mesa de sinuca completa com múltiplas primitivas (`TRIANGLES`, `TRIANGLE_FAN`, `LINE_STRIP`), projeção isotrópica e manipulação mecânica de taco e mira.

---

## 2. Invariantes Arquiteturais e Geométricos

### Regra 1: Correlação Paramétrica Integral

- **Regra:** Todas as coordenadas da mesa, caçapas, bolas e linhas da quadra devem derivar de grandezas fundamentais (`TABLE_WIDTH = 0.90`, `TABLE_HEIGHT = 0.45`, `CUSHION_THICKNESS = 0.10`).
    - `BAULK_LINE_X = -TABLE_WIDTH / 2.0`
    - `BAULK_D_RADIUS = TABLE_WIDTH / 5.0`
    - `CUE_BALL_INITIAL_POS = (BAULK_LINE_X, 0.0)`
    - `RACK_ORIGIN_X = TABLE_WIDTH / 3.0`
    - `RACK_DX_FACTOR = sqrt(3.0) / 2.0`
- **Evite:** Números mágicos literais no fluxo de geração de geometria.
- **Use:** Expressões algébricas contínuas.

### Regra 2: Separação de VBOs e Otimização de VRAM

- **Regra:** VBOs de posição e cor devem ser fisicamente separados na GPU.
- **Evite:** Intercalar atributos em buffers únicos quando parte dos dados for estática. A animação mecânica de potência do taco deve sobrescrever exclusivamente os 128 bytes de `vbo_cue_pos`, mantendo as cores intactas na VRAM.

### Regra 3: Conformidade com Perfil Estrito OpenGL 4.0

- **Regra:** Código GLSL deve ser compatível com `#version 400 core`.
- **Evite:** Utilizar extensões ou recursos introduzidos em versões superiores da especificação OpenGL.

### Regra 4: Proibição Estrita de Comentários no Código (Zero Inline Comments)

- **Regra:** O código Python do projeto é 100% autoexplicativo e não deve conter comentários (`# ...`). Toda a explicação arquitetural e detalhes de implementação devem constar no `README.md` e no `AGENTS.md`.
- **Evite:** Inserir comentários explicativos inline no código-fonte.
- **Use:** Clean Code, tipagem estática e docstrings contratuais sóbrias.

### Regra 5: Padrão Idiomático Estrito (Código em Inglês, Docstrings em Português)

- **Regra:** Todas as entidades de código (classes, funções, variáveis, constantes, uniforms e atributos) devem ser expressas estritamente em inglês. Docstrings contratuais e arquivos `.md` devem ser expressos em português formal.
- **Evite:** Identificadores em português ou docstrings com mistura idiomática.
- **Use:** API e nomes em inglês (`cue_angle`, `rack_origin`), acompanhados de docstrings em português.

---

## 3. Comandos de Validação e Execução

```bash
make run           # Executa a aplicação em modo Debug (Hot-Reload F4 ativo)
make release       # Executa a aplicação em modo Release otimizado
make test          # Executa a suíte de testes unitários de pipeline e geometria
make check         # Validação estática: Pyright (0 erros) e Ruff (0 alertas)
make clean         # Remoção de caches locais
```
