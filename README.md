# Sinucadas

Jogo 2D interativo de sinuca desenvolvido em Python para a Atividade 02 de Computação Gráfica, utilizando **ModernGL**, **GLFW**, **NumPy** e **PyGLM** sobre o perfil estrito **OpenGL 4.0 Core Profile**.

---

## 🎮 Como Jogar e Controles

O jogo conta com controles completos via teclado para rotação ágil e de alta precisão, dosagem de força e execução de tacadas com física elástica em tempo real.

| Tecla | Ação | Descrição |
| :--- | :--- | :--- |
| `←` / `→` | **Girar Mira (Ágil)** | Rotaciona o taco de sinuca e a linha guia tracejada ao redor da bola branca em velocidade normal (1.75 rad/s). |
| `Shift + ← / →` | **Mira de Precisão** | Modo de ajuste fino (0.35 rad/s, 5x mais suave) para alinhamentos milimétricos em bolas ou caçapas distantes. |
| `A` / `D` | **Ajuste Fino (Teclas Alternativas)** | Micro-ajustes de mira para correções minuciosas de ângulo. |
| `↑` / `↓` | **Dosar Força** | Puxa o taco para trás aumentando a força da tacada (efeito visual de recuo dinâmico do taco) ou diminui a força. |
| `ESPAÇO` | **Tacada** | Aplica o impulso na bola branca na direção e intensidade configuradas. |
| `C` | **Cor do Feltro** | Alterna ciclicamente a cor da mesa em tempo real (Verde, Azul, Vermelho e Preto). |
| `N` | **Dia / Noite** | Alterna entre o modo Dia (salão iluminado) e Noite (holofote focado na mesa com atenuação de luz). |
| `F4` | **Hot-Reload** | Recarrega shaders GLSL em tempo real sem reiniciar a aplicação (disponível no modo Debug). |
| `ESC` | **Sair** | Encerra a aplicação e libera com segurança todos os recursos gráficos alocados na GPU. |

---

## 🎱 Mecânicas e Modelo Físico

1. **Mira Guiada Tracejada**: Uma linha tracejada (`moderngl.LINES`) projeta a trajetória planejada da tacada à frente da bola branca.
2. **Animação Conicidade e Recuo do Taco**: O taco é desenhado com `moderngl.TRIANGLES` com conicidade e gradiente de madeira (marfim, madeira dourada e base escura). Ao segurar `↑`, o buffer dinâmico de vértices atualiza o recuo físico do taco.
3. **Colisões Elásticas Bola-Bola**: Algoritmo de resolução de contato círculo-círculo com separação de sobreposição geométrica e conservação de momento linear ($e = 0.96$). Executa 3 sub-iterações por frame para estabilidade perfeita durante o estouro do triângulo de 15 bolas.
4. **Encaçapamento Inteligente**: Bolas numeradas que entram no raio das 6 caçapas são marcadas como encaçapadas e removidas do jogo. Se a bola branca cair em uma caçapa, a falta é acusada e ela é reposicionada automaticamente na marca de saída.
5. **Atrito Linear do Feltro e Tabelas**: Todas as bolas ativas sofrem desaceleração gradual exponencial compatível com o delta time e rebatem elasticamente nas 4 tabelas de madeira.
6. **Projeção Isotrópica Inteligente**: O vertex shader utiliza projeção bidimensional que adapta a escala dinamicamente ao aspecto da janela. A mesa nunca transborda (mesmo em janelas muito altas e estreitas) e as bolas mantêm circularidade absoluta sem distorção.

---

## 📁 Estrutura do Projeto

- `main.py`: Ponto de entrada, loop principal, pooling de eventos contínuos e troca de buffers.
- `graphics.py`: Compilação de shaders, inicialização de geometria (VAO/VBO/EBO) de múltiplas primitivas (tabelas, feltro, caçapas, bolas, taco cônico e linha de mira tracejada).
- `gameplay.py`: Estado das 16 bolas, rotação da mira (ágil e precisão), dosagem de força, atrito do feltro, rebotes e caçapas.
- `physics.py`: Algoritmos geométricos computacionais 2D (estruturas Point e Polygon, orientação de trios de pontos, teste de inclusão ponto em polígono, colisão elástica e detecção de caçapas).
- `window.py`: Inicialização da janela GLFW, callbacks de teclado e redimensionamento de viewport.
- `environment.py`: Utilitário universal de runtime (compilação segura, observer de hot-reload, projeção isotrópica e limpeza determinística).
- `shaders/shader.vert`: Vertex shader com rotação 2D na GPU e projeção bidimensional.
- `shaders/shader.frag`: Fragment shader com atenuação de iluminação para alternância dia/noite.
- `Makefile`: Orquestrador de compilação, execução, testes e análise estática de código.

---

## 🚀 Como Executar

### Pré-requisitos & Ambiente Automático (`uv`)

O ambiente é gerenciado pelo **`uv`** com o mecanismo `--system-site-packages` (dispensando ativação manual com `source`):

```bash
uv venv --system-site-packages && uv sync
```

### Modos de Execução

Executar pelo Makefile (que chama o `uv run` automaticamente):

```bash
make run      # Executa o jogo em modo Debug (Hot-Reload ativo via F4)
make release  # Executa o jogo em modo Release (máxima performance)
make test     # Executa os testes unitários de física e geometria
make check    # Executa a verificação estática com Ruff e Pyright
```

Pressione **F4** durante a partida para recompilar shaders em tempo real.

Pelo Makefile:
```bash
make run
```

Direto via Python:
```bash
python3 main.py
```

#### Modo Release (Otimizado — Hot-Reload Desativado)

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

Valida geometria computacional, física elástica, compilação de shaders e estado do jogo:

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
