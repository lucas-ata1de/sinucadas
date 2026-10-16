# Sinucadas

Projeto prático de Computação Gráfica desenvolvido em Python utilizando **ModernGL**, **GLFW**, **NumPy** e **PyGLM** (OpenGL 4.0 Core Profile).

## 📁 Estrutura do Projeto

- `main.py`: Ponto de entrada e laço principal da aplicação.
- `environment.py`: Utilitário universal de runtime gráfico (janelas GLFW, Observer de hot-reload, compilação segura de shaders e gerenciamento determinístico de recursos).
- `window.py`: Criação de janela, tratamento de redimensionamento do framebuffer e callbacks de entrada.
- `graphics.py`: Módulo de renderização, compilação de shaders e primitivas geométricas (VAO/VBO/EBO).
- `gameplay.py`: Lógica de estado do jogo e movimentação da bola.
- `physics.py`: Física e geometria computacional 2D (testes de orientação e inclusão ponto em polígono).
- `shaders/`: Arquivos de código-fonte dos shaders GLSL.
- `moderngl.sh`: Script utilitário para atalho XDG no Linux e registro de ícone.

## 🚀 Como Executar

Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

### Modos de Execução

O jogo suporta execução em modo Debug e Release tanto pelo Makefile quanto pela linha de comando direta.

#### Modo Debug (Padrão — Hot-Reload Ativo)

Pressione a tecla **F4** durante a partida para recompilar os shaders da pasta `shaders/` em tempo real sem fechar a janela.

Executar via Makefile:
```bash
make run
```

Executar diretamente via Python:
```bash
python3 main.py
```

#### Modo Release (Otimizado — Hot-Reload Desativado)

Executar via Makefile:
```bash
make release
```

Executar diretamente via Python:
```bash
python3 main.py --release
```

### Testes de Sanidade dos Módulos

Os módulos auxiliares possuem testes de sanidade integrados que validam geometria, shaders e física.

Executar via Makefile:
```bash
make test
```

Executar manualmente cada módulo:
```bash
python3 physics.py
python3 graphics.py
python3 gameplay.py
```

## ⌨️ Controles

- **F4:** Dispara a recarga a quente dos shaders e reconstrói o pipeline gráfico (disponível no modo Debug).
- **ESC:** Fecha a aplicação e libera os recursos gráficos.
