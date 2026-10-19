# Planejamento & Recursos — Atividade 03 (Jogo 2D Animado)

Jogo bidimensional de sinuca animado com física e tempo real em ModernGL e GLFW sob OpenGL 4.0 Core Profile.

---

## 🎱 Recursos Implementados

### 1. Motor Físico & Cinemática
* **Animação por $\Delta t$**: Cinemática temporal contínua e passo máximo para evitar saltos.
* **Colisão Círculo-Círculo**: Separação geométrica e conservação de momento linear ($e = 0.96$).
* **Rebote em Tabelas**: Reflexão elástica nas 4 bordas da mesa com restituição física.
* **Atrito do Feltro**: Desaceleração exponencial realista por rolagem.
* **Encaçapamento**: Detecção nas 6 caçapas, contagem de bolas e penalidade de falta na branca.

### 2. Primitivas Gráficas & Shaders
* **Múltiplas Primitivas**: `TRIANGLES` (mesa e taco), `TRIANGLE_FAN` (bolas e caçapas), `LINE_STRIP` (linhas de baulk) e `LINES` (mira).
* **Reaproveitamento de VBO**: Círculo unitário único compartilhado por todas as bolas e caçapas.
* **Shaders Customizados**: Vertex shader com projeção isotrópica e fragment shader com atenuação.
* **Ambiente Visual**: Alternância de cor do feltro (`C`), Dia/Noite (`N`) e Hot-Reload (`F4`).

### 3. Jogabilidade & Controles
* **Taco e Mira**: Rotação ágil (`←`/`→` ou `A`/`D`) e precisão (`Shift`); dosagem de força (`↑`/`↓` ou `W`/`S`) com modo suave (`Shift`).
* **Disparo (`ESPAÇO`)**: Aplicação de impulso físico vetorial na bola branca.

---

## 📌 Próximos Passos (Requisitos da Atividade 03)

1. **Estados do Jogo**: Máquina de estados (Início, Em Andamento, Pausado, Fim de Jogo com reinício).
2. **Taxa de Quadros & VSync**: Alternância de VSync (`glfw.swap_interval`) e FPS na barra de título.
3. **Placar em Geometria**: Renderizar bolas encaçapadas/vidas diretamente na cena com primitivas.
4. **Animação Autônoma**: Elemento auxiliar com movimentação periódica independente.
5. **Relatório & Screenshots**: Capturas de tela dos estados e documento PDF para o Moodle.
