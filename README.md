# Sinucadas — Cena 2D Interativa

Cena 2D interativa de sinuca desenvolvida em Python para a **Atividade 02 de Computação Gráfica**, utilizando **ModernGL**, **GLFW** e **NumPy** sobre o perfil estrito **OpenGL 4.0 Core Profile**.

---

## 🎯 Atendimento aos Requisitos do Enunciado

| Requisito do Enunciado | Implementação no Projeto | Primitiva / Recurso Técnico |
| :--- | :--- | :--- |
| **Composição da Cena** | Mesa completa: tabelas de madeira, feltro, 6 caçapas, marcações de baulk ("D" de sinuca), triângulo de 15 bolas coloridas, bola branca e taco de sinuca com mira tracejada. | Composição rica de múltiplos elementos visuais. |
| **Múltiplas Primitivas** | Construção da cena utilizando 4 primitivas distintas do OpenGL. | `TRIANGLES` (mesa, bordas e taco), `TRIANGLE_FAN` (círculos das caçapas e bolas), `LINE_STRIP` (linha de saída e arco de baulk), `LINES` (mira tracejada). |
| **Reaproveitamento de Geometria** | Um único VBO circular unitário (`vao_circle`) é gerado na inicialização e reutilizado para desenhar 22 círculos distintos (6 caçapas + 16 bolas). | `u_offset`, `u_scale` e `u_color` aplicados no Vertex e Fragment Shader. |
| **Alternância Dia / Noite** | Tecla `N` comuta o estado global da cena entre iluminação diurna e ambiente noturno (holofote). | `ctx.clear(0.82, 0.82, 0.85)` / `ctx.clear(0.05, 0.05, 0.08)` + uniform `u_attenuation` (1.0 vs 0.40). |
| **Alteração Dinâmica de Cores** | Tecla `C` altera em tempo real a cor do feltro da mesa ciclando entre 4 paletas clássicas. | Verde Clássico, Azul Royal, Vermelho Bordô e Preto Carbono via uniform `u_color`. |
| **Movimentação mecânica (Setas)** | Setas do teclado controlam a orientação angular e a translação mecânica do taco em relação à bola branca. | `←` / `→` para rotação contínua (com ajuste fino via `Shift`); `↑` / `↓` para recuo/aproximação do taco. |
| **OpenGL Core Profile** | Pipeline programável estrito (OpenGL 4.0 Core), sem recursos legados (`glBegin`, `glEnd`, matrizes embutidas). | ModernGL com shaders GLSL 400 Core customizados (`shader.vert` e `shader.frag`). |

---

## 🎮 Controles e Interação

| Tecla | Ação | Descrição |
| :--- | :--- | :--- |
| `←` / `→` | **Girar Taco (Ágil)** | Rotaciona o taco de sinuca e a linha guia tracejada ao redor da bola branca (1.75 rad/s). |
| `Shift + ← / →` | **Giro de Precisão** | Modo de ajuste fino (0.35 rad/s, 5x mais suave) para alinhamento milimétrico da mira. |
| `A` / `D` | **Giro Alternativo** | Micro-ajustes angulares utilizando a mão esquerda. |
| `↑` / `↓` | **Distância do Taco (Ágil)** | Puxa o taco para trás ou aproxima-o da bola branca (ajuste mecânico normal). |
| `Shift + ↑ / ↓` | **Distância com Precisão** | Ajuste fino e suave do recuo/aproximação mecânica do taco. |
| `W` / `S` | **Distância (Teclas Alternativas)** | Micro-ajustes de distância utilizando a mão esquerda. |
| `C` | **Cor do Feltro** | Alterna ciclicamente a cor da mesa em tempo real (Verde, Azul, Vermelho e Preto). |
| `N` | **Dia / Noite** | Alterna entre o modo Dia (salão claro) e Noite (mesa com iluminação focada e fundo escuro). |
| `F4` | **Hot-Reload** | Recarrega shaders GLSL em tempo real sem fechar a janela (modo Debug). |
| `ESC` | **Sair** | Encerra a aplicação e libera com segurança todos os recursos gráficos alocados na GPU. |

---

## 📁 Estrutura do Projeto

- `main.py`: Ponto de entrada, loop de renderização, pooling de eventos contínuos e tratamento de teclas.
- `graphics.py`: Compilação de shaders, geometrias (VAO/VBO/EBO), múltiplas primitivas (`TRIANGLES`, `TRIANGLE_FAN`, `LINE_STRIP`, `LINES`), projeção isotrópica e renderização da cena.
- `window.py`: Inicialização da janela GLFW em OpenGL 4.0 Core, callbacks e gerenciamento do viewport ModernGL.
- `environment.py`: Utilitário de ambiente e cursor XCURSOR para prevenção de distorções visuais no Wayland/X11.
- `shaders/shader.vert`: Vertex shader com rotação 2D na GPU e projeção bidimensional isotrópica.
- `shaders/shader.frag`: Fragment shader com modulação de cor e atenuação de iluminação para modo Dia/Noite.
- `Makefile`: Orquestrador de compilação, execução, testes unitários e análise estática de código.

---

## 🚀 Como Executar

### Pré-requisitos & Ambiente Automático (`uv`)

O ambiente é gerenciado pelo **`uv`** com o mecanismo `--system-site-packages` (dispensando ativação manual com `source`):

```bash
uv venv --system-site-packages && uv sync
```

### Modos de Execução

Você pode executar a aplicação tanto pelo Makefile (que chama o `uv run` automaticamente) quanto diretamente via Python.

#### Modo Debug (Padrão — Hot-Reload Ativo)

Executa a cena em modo de desenvolvimento. Pressione **`F4`** durante a execução para recompilar shaders em tempo real sem reiniciar a aplicação ou fechar a janela:

Pelo Makefile:
```bash
make run
```

Direto via Python:
```bash
python3 main.py
```

#### Modo Release (Otimizado — Hot-Reload Desativado)

Executa a cena em modo de apresentação focado em máxima performance e estabilidade:

Pelo Makefile:
```bash
make release
```

Direto via Python:
```bash
python3 main.py --release
```

---

## 🧪 Testes e Verificação de Qualidade

### Testes Unitários de Módulos

Valida o pipeline gráfico, inicialização das primitivas e ambiente de janela:

```bash
make test
```

### Verificação Estática de Tipagem e Sintaxe

Executa checagem estática de tipos com **Pyright** e análise de código com **Ruff**:

```bash
make check
```

Alias:
```bash
make lint
```

### Limpeza de Caches Temporários

Remove recursivamente pastas `__pycache__` e arquivos `*.pyc`:

```bash
make clean
```
