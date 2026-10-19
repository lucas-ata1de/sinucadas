# 📋 TODO — Atividade 02: Sinucadas (Cena 2D Interativa)

Planejamento e acompanhamento das etapas de desenvolvimento para a **Atividade 02 de Computação Gráfica**.

---

## 🎯 Requisitos Oficiais do Enunciado

- [x] **Arquitetura modular em camadas:** (`main`, `graphics`, `window`, `environment`).
- [x] **Shaders customizados em GLSL:** (`shader.vert` e `shader.frag`) em OpenGL 4.0 Core Profile.
- [x] **Projeção Isotrópica Inteligente:** Adaptação dinâmica ao aspect ratio da janela sem distorção das esferas e sem transbordamento.
- [x] **Hot-reload de shaders em tempo real:** Suporte à recompilação ao vivo via tecla `F4` (modo Debug).
- [x] **Múltiplas Primitivas:**
  - [x] `moderngl.TRIANGLES` (feltro da mesa, moldura das 4 tabelas de madeira e taco cônico de sinuca).
  - [x] `moderngl.TRIANGLE_FAN` (leque circular para as 6 caçapas e 16 bolas).
  - [x] `LINE_STRIP` (linha de saída e arco "D" de baulk da mesa).
  - [x] `moderngl.LINES` (linha guia tracejada de mira da bola branca).
- [x] **Reaproveitamento de Geometria:**
  - [x] Buffer de círculo unitário único (`vao_circle`) reutilizado para desenhar 22 círculos (6 caçapas + 16 bolas) via uniforms de escala, translação e cor (`u_offset`, `u_scale`, `u_color`).
  - [x] Buffer retangular indexado com EBO (`vao_table`) para as tabelas e o feltro.
- [x] **Alternância Global de Estado (Dia/Noite com Tecla N):**
  - [x] Transição de cor de fundo com `ctx.clear` (dia claro vs noite escuro).
  - [x] Atenuação de cor dos elementos via `uniform float u_attenuation` no fragment shader (1.0 vs 0.40).
- [x] **Alteração Dinâmica de Cores (Tecla C):**
  - [x] Ciclo de 4 cores do feltro da mesa em tempo real (Verde Clássico, Azul Royal, Vermelho Bordô, Preto Carbono).
- [x] **Movimentação Mecânica por Teclado:**
  - [x] Setas `←` e `→` (ou `A`/`D`) para rotação do taco de sinuca e linha de mira ao redor da bola branca.
  - [x] `Shift` + `←`/`→` para rotação de alta precisão (5x mais suave).
  - [x] Setas `↑` e `↓` (ou `W`/`S`) para translação mecânica/distância do taco em relação à bola branca.
- [x] **Qualidade e Estilo:**
  - [x] 100% em conformidade com Ruff (PEP 8, sem warnings).
  - [x] 100% em conformidade com Pyright (0 erros, tipos estritos).
- [ ] **Entrega e Relatório:**
  - [ ] Captura de screenshots dos modos Dia e Noite.
  - [ ] Redação do relatório PDF formal com explicação da arquitetura.
  - [ ] Preparação conceitual para a defesa oral com o professor.

---

## 🧭 Fases de Execução

1. [x] **Fase 1:** Geometria 2D, Múltiplas Primitivas, Shaders Limpos e Correção de Aspect Ratio.
2. [x] **Fase 2:** Shaders, Uniforms de Atenuação e Alternância Dia/Noite + Cores do Feltro.
3. [x] **Fase 3:** Taco de Sinuca, Linha Guia e Controles Mecânicos de Mira e Recuo via Teclado.
4. [x] **Fase 4:** Simplificação Arquitetural e Segregação de Branches (`atv-02` para Cena 2D; `atv-03` para Jogo 2D Animado).
5. [ ] **Fase 5:** Screenshots, Relatório em PDF e Preparação para a Defesa Oral.
