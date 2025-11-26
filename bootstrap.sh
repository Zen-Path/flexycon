#!/usr/bin/env sh

# Argument Parsing & Help

show_help() {
    echo "Usage: ./bootsrap.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -v, --verbose   Show detailed output during installation."
    echo "  -h, --help      Show this help message and exit."
    echo ""
}

VERBOSE="false"

# Loop through all arguments passed to the script
for arg in "$@"; do
    case $arg in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            ;;
    esac
done

if [ "$VERBOSE" = true ]; then
    PIP_FLAGS=""
    APP_FLAGS="--verbose"
else
    PIP_FLAGS="-q"
    APP_FLAGS=""
fi

log() {
    if [ "$VERBOSE" = true ]; then
        echo "$@"
    fi
}

# Platform Selection

VENV_DIR=".venv"

# Check if the Windows 'Scripts' folder exists, otherwise assume Unix
if [ -d "$VENV_DIR/Scripts" ]; then
    VENV_BIN="$VENV_DIR/Scripts"
else
    VENV_BIN="$VENV_DIR/bin"
fi

VENV_PIP="$VENV_BIN/pip"
VENV_PYTHON="$VENV_BIN/python"
PYTHON="python3"

# Main

if [ ! -d "$VENV_DIR" ]; then
    log "🐍 Creating Python venv in '$VENV_DIR'..."
    $PYTHON -m venv $VENV_DIR
fi

log "🔧 Installing current project and dependencies..."

$VENV_PIP install $PIP_FLAGS -e .

$VENV_PYTHON flexycon.py $APP_FLAGS setup
$VENV_PYTHON flexycon.py $APP_FLAGS install

log "✅ Bootsrap complete."
