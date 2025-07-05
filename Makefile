.PHONY: clean setup init-submodules install help

PYTHON ?= /opt/homebrew/bin/python3
VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin

# Should be the value of `package_dir` in setup.py
PACKAGE_DIR := "dotfiles/src"

# System package dependencies
BREW_DEPS := python3 node dotdrop

CLEAN_TARGETS = \
	.venv \
	venv \
	.mypy_cache \
	.pytest_cache \
	__pycache__ \
	dist \
	build \
	*.egg-info \
	node_modules \
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
	@$(MAKE) init-submodules
	@echo "✅ Setup completed successfully."

init-submodules:
	@if [ ! -f .gitmodules ]; then \
		echo "No git submodules found. Skipping."; \
	else \
		echo "Initializing submodules..."; \
		git submodule init || { echo "Failed to initialize submodules"; exit 1; }; \
		echo "Updating submodules..."; \
		if ! git submodule update --recursive --remote; then \
			echo "Error: Unable to fetch submodules. Please check your network or Git server access."; \
			exit 1; \
		fi; \
	fi

install:
	@case "$$(uname)" in \
		Darwin) \
			echo "🖥️ Detected macOS system."; \
			if ! command -v brew >/dev/null 2>&1; then \
				echo "❌ Homebrew is not installed. Please install it from https://brew.sh/"; \
				exit 1; \
			fi; \
			\
			for dep in $(BREW_DEPS); do \
				if ! command -v "$$dep" >/dev/null 2>&1; then \
					read -p "🔍 '$$dep' is not installed. Install it now? [y/N]: " ans; \
					\
					case "$$ans" in \
						y|Y) echo "➡️ Installing $$dep..."; brew install "$$dep" ;; \
						*) echo "⚠️ Skipping $$dep";; \
					esac; \
				else \
					echo "✅ '$$dep' is already installed."; \
				fi; \
			done \
			;; \
		*) \
			echo "ℹ️ Non-macOS system detected. Skipping Homebrew setup."; \
			;; \
	esac

	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "🐍 Creating Python venv in '$(VENV_DIR)'..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

	@echo "♻️ Updating pip..."
	@$(VENV_BIN)/pip install --upgrade pip

	@if [ -f "requirements.txt" ]; then \
		echo "📦 Installing Python dependencies..."; \
		$(VENV_BIN)/pip install -r requirements.txt; \
	else \
		echo "⚠️ Python dependencies not found."; \
	fi

	echo "🔧 Installing current project in editable mode...";
	@if [ ! -d "$(PACKAGE_DIR)" ]; then \
		mkdir -p "$(PACKAGE_DIR)"; \
	fi
	@$(VENV_BIN)/pip install -e .

	@echo "📦 Installing npm packages..."
	@npm install

	@echo "📦 Installing pre-commit hooks..."
	@$(VENV_BIN)/pre-commit install --install-hooks

help:
	@echo "Available make targets:"
	@echo "  setup       		Setup project and init git submodules"
	@echo "  install			Create Python venv, install Python, project dependencies"
	@echo "  clean				Remove temporary/project files and venv"
	@echo "  init-submodules	Initialize and fetch git submodules"
	@echo "  help				Show this help message"
