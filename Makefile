.POSIX:
.SILENT:

MAKEFLAGS += --no-print-directory -s

# ----------------------------------------------------------------
# Makefile: Sinucadas (Atividade 02 — OpenGL 4.0 Core)
# ----------------------------------------------------------------

PYTHON = $(shell which uv > "/dev/null" 2>&1 && echo "uv run --quiet python -B" || echo "python3 -B")
export PYTHONDONTWRITEBYTECODE = 1
export RUFF_CACHE_DIR = /tmp/ruff-cache

.PHONY: all run debug release test check lint clean help

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
	cmd "check"          "Verifica erros estáticos de tipagem (Pyright) e lint/estilo (Ruff)"; \
	cmd "lint"           "Alias para 'make check'"; \
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
### STATIC ANALYSIS & LINTING
### ================================
check:
	echo "🔍 [1/2] Verificando sintaxe e estilo com Ruff..."
	if which uv > "/dev/null" 2>&1; then \
		uv run ruff check --cache-dir /tmp/ruff-cache --select E,F,W --ignore E501 . && echo "  ✅ Ruff: nenhuma violação de sintaxe encontrada."; \
	elif which ruff > "/dev/null" 2>&1; then \
		ruff check --cache-dir /tmp/ruff-cache --select E,F,W --ignore E501 . && echo "  ✅ Ruff: nenhuma violação de sintaxe encontrada."; \
	else \
		echo "  ⚠️  Ruff não encontrado. Pulando verificação Ruff."; \
	fi
	echo "🔍 [2/2] Verificando tipagem estática com Pyright..."
	if which uv > "/dev/null" 2>&1; then \
		uv run pyright . && echo "  ✅ Pyright: 0 erros de tipagem encontrados."; \
	elif which pyright > "/dev/null" 2>&1; then \
		pyright . && echo "  ✅ Pyright: 0 erros de tipagem encontrados."; \
	elif which npx > "/dev/null" 2>&1; then \
		npx --yes pyright . && echo "  ✅ Pyright: 0 erros de tipagem encontrados."; \
	else \
		echo "  ⚠️  Pyright/npx não encontrado. Instale Node.js/npx ou pyright para checar tipos."; \
	fi
	echo "✨ Verificação concluída com sucesso!"

lint: check

### ================================
### CLEANUP
### ================================
clean:
	echo "🧹 Limpando caches temporários (__pycache__, *.pyc, .ruff_cache)..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2> "/dev/null" || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2> "/dev/null" || true
	find . -type f -name "*.pyc" -delete 2> "/dev/null" || true
	echo "✅ Caches limpos com sucesso!"
