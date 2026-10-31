# Planejamento & Recursos — Atividade 02 (Cena 2D Interativa)

Cena bidimensional de mesa de sinuca interativa implementada em ModernGL e GLFW sob OpenGL 4.0 Core Profile.

---

## 🎨 Recursos Implementados

### 1. Primitivas Gráficas & Geometria

- **`TRIANGLES`**: Mesa, tabelas de madeira e taco cônico com indexação (EBO).
- **`TRIANGLE_FAN`**: Reutilização de VBO unitário para 22 círculos (6 caçapas e 16 bolas).
- **`LINE_STRIP`**: Marcações de baulk (linha de saída e arco do "D").
- **`LINES`**: Linha guia tracejada de mira.
- **Projeção Isotrópica**: Correção dinâmica de aspecto sem distorção das esferas.

### 2. Iluminação & Shaders

- **Pipeline GLSL 400 Core**: Shaders dedicados (`shader.vert` e `shader.frag`).
- **Modo Dia/Noite (`N`)**: `ctx.clear` contextual e atenuação de iluminação via `u_attenuation`.
- **Cor do Feltro Dinâmica (`C`)**: Comutação em tempo real entre 4 temas clássicos.
- **Hot-Reload (`F4`)**: Recompilação de shaders em tempo real sem reiniciar a aplicação.

### 3. Interação Mecânica do Taco

- **Rotação (`←`/`→` ou `A`/`D`)**: Giro contínuo ao redor da bola branca (com `Shift` para precisão 5x mais suave).
- **Distância do Taco (`↑`/`↓` ou `W`/`S`)**: Avanço e recuo mecânico proporcional (com `Shift` para precisão fina).

---

## 📌 Próximos Passos (Entrega)

1. Capturar screenshots da cena nos modos Dia e Noite.
2. Elaborar o relatório PDF formal com a arquitetura e divisão de tarefas.
3. Empacotar o arquivo final `.zip` para submissão no Moodle.
