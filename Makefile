.POSIX:
.SILENT:

MAKEFLAGS += --no-print-directory -s

# ----------------------------------------------------------------
# Makefile: Sinucadas (Atividade 02 — OpenGL 4.0 Core)
# ----------------------------------------------------------------

PYTHON = python3 -B
export PYTHONDONTWRITEBYTECODE = 1

.PHONY: all run debug release test clean help

all: run

### ================================
### HELP & DOCUMENTATION
### ================================
help:
	cmd() { printf "    \033[36mmake %-18s\033[0m %s\n" "$$1" "$$2"; }; \
	sec() { printf "\n  \033[1;33m%s\033[0m\n" "$$1"; }; \
	printf "\n  \033[1;37mSinucadas (Atividade 02) — Jogo 2D em ModernGL\033[0m\n"; \
	printf "  ============================================================\n"; \
	sec "Execução & Modos:"; \
	cmd "run"            "Executa o jogo em modo Debug padrão (Hot-Reload ativo via F4)"; \
	cmd "debug"          "Executa o jogo explicitamente em modo Debug (Hot-Reload ativo)"; \
	cmd "release"        "Executa o jogo em modo Release (--release, Hot-Reload inativo)"; \
	sec "Testes & Sanidade:"; \
	cmd "test"           "Executa testes unitários dos módulos (physics, graphics, gameplay)"; \
	sec "Manutenção & Limpeza:"; \
	cmd "clean"          "Remove recursivamente caches temporários (__pycache__, *.pyc)"; \
	echo ""

### ================================
### EXECUTION & TESTING
### ================================
run: debug

debug:
	$(PYTHON) main.py

release:
	$(PYTHON) main.py --release

test:
	echo "🧪 Executando testes unitários do Sinucadas..."
	$(PYTHON) physics.py
	$(PYTHON) graphics.py
	$(PYTHON) gameplay.py
	echo "✅ Todos os testes de módulos foram aprovados com sucesso!"

### ================================
### CLEANUP
### ================================
clean:
	echo "🧹 Limpando caches e bytecode Python (__pycache__, *.pyc)..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	echo "✅ Caches limpos com sucesso!"
