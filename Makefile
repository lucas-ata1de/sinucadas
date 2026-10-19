.POSIX:
.SILENT:

MAKEFLAGS += --no-print-directory -s

# ----------------------------------------------------------------
# Makefile: Sinucadas (Atividade 03 — OpenGL 4.0 Core)
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
	printf "\n  \033[1;37mSinucadas (Atividade 03) — 2D Game in ModernGL\033[0m\n"; \
	printf "  ============================================================\n"; \
	sec "Execution & Modes:"; \
	cmd "run"            "Runs the game in standard Debug mode (Hot-Reload active via F4)"; \
	cmd "debug"          "Runs the game explicitly in Debug mode (Hot-Reload active)"; \
	cmd "release"        "Runs the game in Release mode (--release, Hot-Reload disabled)"; \
	sec "Tests & Sanity:"; \
	cmd "test"           "Runs unit tests for all modules (environment, window, physics, graphics, gameplay)"; \
	cmd "check"          "Checks static types (Pyright) and style/lint (Ruff)"; \
	cmd "lint"           "Alias for 'make check'"; \
	sec "Maintenance & Cleanup:"; \
	cmd "clean"          "Recursively removes temporary caches (__pycache__, *.pyc)"; \
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
	echo "🧪 Executing Sinucadas unit tests..."
	$(PYTHON) environment.py
	$(PYTHON) window.py
	$(PYTHON) physics.py
	$(PYTHON) graphics.py
	$(PYTHON) gameplay.py
	echo "✅ All module tests passed successfully!"

### ================================
### STATIC ANALYSIS & LINTING
### ================================
check:
	echo "🔍 [1/2] Checking syntax and style with Ruff..."
	if which uv > "/dev/null" 2>&1; then \
		uv run ruff check --cache-dir /tmp/ruff-cache --select E,F,W --ignore E501 . && echo "  ✅ Ruff: no syntax violations found."; \
	elif which ruff > "/dev/null" 2>&1; then \
		ruff check --cache-dir /tmp/ruff-cache --select E,F,W --ignore E501 . && echo "  ✅ Ruff: no syntax violations found."; \
	else \
		echo "  ⚠️  Ruff not found. Skipping Ruff checks."; \
	fi
	echo "🔍 [2/2] Checking static types with Pyright..."
	if which uv > "/dev/null" 2>&1; then \
		uv run pyright . && echo "  ✅ Pyright: 0 typing errors found."; \
	elif which pyright > "/dev/null" 2>&1; then \
		pyright . && echo "  ✅ Pyright: 0 typing errors found."; \
	elif which npx > "/dev/null" 2>&1; then \
		npx --yes pyright . && echo "  ✅ Pyright: 0 typing errors found."; \
	else \
		echo "  ⚠️  Pyright/npx not found. Install Node.js/npx or pyright to check types."; \
	fi
	echo "✨ Verification completed successfully!"

lint: check

### ================================
### CLEANUP
### ================================
clean:
	echo "🧹 Cleaning temporary caches (__pycache__, *.pyc, .ruff_cache)..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2> "/dev/null" || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2> "/dev/null" || true
	find . -type f -name "*.pyc" -delete 2> "/dev/null" || true
	echo "✅ Caches cleaned successfully!"
