.PHONY: clean setup init-submodules install help

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
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "✅ Virtual environment already exists at '$(VENV_DIR)'."; \
	else \
		echo "🐍 Creating Python virtual environment in '$(VENV_DIR)'..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

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
	@echo "  setup       		Setup project and init git submodules"
	@echo "  install			Create Python venv, install Python, project dependencies"
	@echo "  clean				Remove temporary/project files and venv"
	@echo "  init-submodules	Initialize and fetch git submodules"
	@echo "  help				Show this help message"
