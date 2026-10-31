# Planejamento & Recursos — Atividade 03 (Jogo 2D Animado)

Jogo bidimensional multiplayer de sinuca animado em tempo real com ModernGL e GLFW sob perfil estrito **OpenGL 4.0 Core Profile**.

---

## 🎱 Recursos Implementados (100% dos Requisitos Técnicos + Multiplayer)

### 1. Motor Físico, Anti-Tunelamento & Cinemática (`physics.py` & `gameplay.py`)

- **Animação por $\Delta t$ e Passo Máximo (`MAX_DT = 0.05`)**: Velocidades em unidades por segundo, independentes de taxa de quadros, evitando saltos ao arrastar a janela.
- **Sub-stepping Temporal (Anti-Tunelamento)**: Subdivisão adaptativa de $\Delta t$ (4 a 16 sub-passos por quadro) garantindo que nenhuma bola avance mais que $0.45 R$ por passo e impedindo tunelamento em tacadas de alta velocidade.
- **Colisão Círculo-Círculo**: Separação geométrica de sobreposição e conservação de momento linear elástico ($e = 0.96$).
- **Rebote nas Tabelas & Bocas das Caçapas**: Reflexão elástica nas 4 bordas com aberturas reais nas 6 caçapas e funil radial de captura nas bordas.
- **Raycast Analítico de Mira (Ghost Ball)**: Interseção raio-círculo e raio-tabela em tempo real indicando exatamente onde a bola branca tocará o alvo e a direção resultante da bola atingida.
- **Atrito de Rolagem**: Desaceleração exponencial contínua ($\mu^{60 \Delta t}$) e parada determinística.

### 2. Sistema Multiplayer, Pontuação de Sinuca & Máquina de Estados (`gameplay.py` & `main.py`)

- **Turnos Alternados (P1 vs P2)**:
    - **Jogador 1 (Azul Safira)** e **Jogador 2 (Vermelho Rubi)** alternam turnos a cada tacada.
    - Encaçapar ao menos uma bola legal sem cometer falta mantém a vez com o jogador atual; errar ou cometer falta passa o turno para o oponente assim que as bolas param.
- **Sistema de Pontuação de Sinuca**:
    - Cada bola numerada concede seu valor nominal (**1 a 15 pontos**) ao jogador da vez.
    - **Faltas** (encaçapar a bola branca ou encaçapar a Bola 8 prematuramente) concedem **+4 pontos de bônus** ao adversário e descontam 1 vida.
    - Ao limpar as 15 bolas (`VICTORY`), o vencedor é determinado pela maior pontuação acumulada.
- **Placar no Título da Janela (`main.py`)**:
    - Exibe em tempo real: turno ativo (`Vez: P1 Azul` / `P2 Vermelho`), placar detalhado (`Placar: P1 X pts (N) x P2 Y pts (M)`), vidas restantes, V-Sync (`ON`/`OFF`) e FPS.
- **5 Estados Completos**:
    - `START` (Início), `PLAYING` (Em Andamento), `PAUSED` (Pausado — tecla `P`), `VICTORY` (Vitória com anúncio do vencedor) e `GAME_OVER` (Derrota).

### 3. Primitivas Gráficas, Taco Colorido por Jogador & HUD Geométrico (`graphics.py`)

- **Taco e Mira com Cores por Jogador**:
    - O VBO estático do taco utiliza luminância neutra nos vértices e recebe modulação cromática via `u_color` no shader: **Azul Safira** para o Jogador 1 e **Vermelho Rubi** para o Jogador 2 (acompanhado pela linha guia e Ghost Ball na mesma paleta).
- **Reaproveitamento Estrito de VBOs**: Todos os VBOs (`table`, `circle`, `ring`, `quad`, `lines`, `aim`, `cue`) são criados **apenas uma vez** na inicialização, sem `vbo.write()` por quadro.
- **Múltiplas Primitivas OpenGL**:
    - `moderngl.TRIANGLES`: Feltro, tabelas de madeira, taco cônico e barras do HUD.
    - `moderngl.TRIANGLE_FAN`: 16 bolas, 6 caçapas, emblemas de jogador, bolas do placar e indicadores de vida.
    - `moderngl.LINE_STRIP`: Linha de baulk e semicírculo do "D".
    - `moderngl.LINE_LOOP`: Ghost Ball pulsante, anel de turno ativo, halos luminosos das caçapas e molduras do placar.
    - `moderngl.LINES`: Linha guia tracejada escalável e vetor normal de deflexão.
- **HUD Geométrico Multiplayer na Cena**: Racks separados para P1 e P2 no topo da tela com indicador luminoso pulsante no jogador da vez, medidor de potência de 10 segmentos e 3 indicadores de vida.

---

## 📌 Próximos Passos (Submissão Moodle)

1. Capturar screenshots demonstrando os estados (`START`, `PLAYING` no turno do P1 Azul e P2 Vermelho, `PAUSED`, `VICTORY` / `GAME_OVER`) e modos Dia/Noite.
2. Redigir o relatório PDF formal descrevendo a arquitetura, laço $\Delta t$, sub-stepping anti-tunelamento, regras multiplayer e divisão de tarefas.
3. Empacotar o arquivo `.zip` final para entrega no Moodle.
