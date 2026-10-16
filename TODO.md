# 📋 TODO — Atividade 02: Sinucadas

Planejamento e acompanhamento das etapas de desenvolvimento para a Atividade 02 de Computação Gráfica.

---

## 🎯 Requisitos Oficiais do Enunciado

- [x] Arquitetura modular em camadas (`window`, `graphics`, `physics`, `gameplay`, `environment`).
- [x] Shaders customizados em GLSL (`.vert`, `.frag`) em OpenGL 4.0 Core Profile (`shader.vert` e `shader.frag`).
- [x] Remoção de shaders obsoletos desnecessários (`bola.vert` e `uniquad.vert`).
- [x] Proteção e correção dinâmica de aspect ratio (`uniform float u_aspect`).
- [x] Hot-reload de shaders em tempo real via tecla F4.
- [x] **Múltiplas Primitivas:**
  - [x] `moderngl.TRIANGLES` (feltro da mesa e moldura das 4 tabelas de madeira).
  - [x] `moderngl.TRIANGLE_FAN` (leque circular para as 6 caçapas e 16 bolas).
  - [x] `moderngl.LINE_STRIP` (linha de saída e arco "D" da mesa).
- [x] **Reaproveitamento de Geometria:**
  - [x] Buffer de círculo único na VRAM instanciado/desenhado para todas as bolas e caçapas.
  - [x] Buffer retangular único para as bordas e feltro.
- [x] **Alternância Global de Estado (Dia/Noite com Tecla N):**
  - [x] Transição de cor de fundo com `ctx.clear`.
  - [x] Atenuação de cor dos elementos via `uniform float u_attenuation` no fragment shader.
- [x] **Alteração Dinâmica de Cores (Tecla C):**
  - [x] Ciclo de 4 cores do feltro da mesa em tempo real (Verde, Azul, Vermelho, Preto).
- [x] **Movimentação Mecânica por Teclado:**
  - [x] Setas `←` e `→` para girar o ângulo de mira do taco ao redor da bola branca.
  - [x] Setas `↑` e `↓` para dosar a força da tacada (recuo visual do taco).
  - [x] Barra de `ESPAÇO` para disparar a tacada na bola branca.
- [x] **Física 2D de Sinuca:**
  - [x] Desaceleração por atrito linear do feltro.
  - [x] Rebote elástico contra as 4 tabelas de madeira.
  - [x] Colisão elástica bidimensional entre bolas.
  - [x] Detecção de encaçapamento (bola dentro do raio da caçapa).
- [ ] **Entrega e Relatório:**
  - [ ] Captura de screenshots dos modos Dia e Noite.
  - [ ] Redação do relatório PDF formal com explicação da arquitetura.
  - [ ] Preparação conceitual para a defesa oral com o professor.

---

## 🧭 Fases de Execução

1. [x] **Fase 1:** Geometria 2D, Múltiplas Primitivas, Shaders Limpos e Correção de Aspect Ratio.
2. [x] **Fase 2:** Shaders, Uniforms de Atenuação e Alternância Dia/Noite + Cores do Feltro.
3. [x] **Fase 3:** Taco de Sinuca, Linha Guia e Controles de Mira/Tiro via Teclado.
4. [x] **Fase 4:** Lógica de Física Completa (Colisões Círculo-Círculo e Caçapas).
5. [ ] **Fase 5:** Screenshots, Relatório em PDF e Preparação para a Defesa Oral.
