.PHONY: clean setup install help

PYTHON ?= /opt/homebrew/bin/python3
VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin

CLEAN_TARGETS = \
	.venv \
	venv \
	.mypy_cache \
	.pytest_cache \
	__pycache__ \
	node_modules \
	dist \
	build \
	*.egg-info \
	.DS_Store

clean:
	@echo "Cleaning up project..."
	@for dir in $(CLEAN_TARGETS); do \
		find . -name "$$dir" -exec rm -rf {} +; \
	done

	@echo "Cleaning up pre-commit hooks..."
	@if [ -d "$(VENV_DIR)" ]; then \
		@$(VENV_BIN)/pre-commit clean; \
	fi

	@echo "Full cleanup complete."

setup:
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "✅ Virtual environment already exists at '$(VENV_DIR)'."; \
	else \
		echo "🐍 Creating Python virtual environment in '$(VENV_DIR)'..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

install:
	@echo "🔧 Ensuring virtual environment is set up..."
	@$(MAKE) setup

	@echo "♻️ Updating pip..."
	@$(VENV_BIN)/pip install --upgrade pip

	@echo "📦 Installing Python dependencies..."
	@$(VENV_BIN)/pip install -r requirements.txt

	@if [ ! -d "src" ]; then \
		mkdir "src"; \
	fi
	@$(VENV_BIN)/pip install -e .

	@echo "📦 Installing npm packages..."
	@npm install

	@echo "📦 Installing pre-commit hooks..."
	@$(VENV_BIN)/pre-commit install --install-hooks

help:
	@echo "Available make targets:"
	@echo "  setup       Create Python virtual environment using $(PYTHON)"
	@echo "  install     Install Python, npm, and pre-commit dependencies"
	@echo "  clean       Remove temporary/project files (safe)"
	@echo "  clean-all   Run clean and remove virtual environments"
	@echo "  help        Show this help message"
