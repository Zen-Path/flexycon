#!/usr/bin/env sh

# CLI ARGS & HELP

show_help() {
    echo "usage: ./bootstrap.sh [OPTIONS]"
    echo ""
    echo "options:"
    echo "  -h, --help      show this help message and exit"
    echo "  -v, --verbose   enable debug output"
    echo ""
}

VERBOSE="false"

# Loop through all arguments passed to the script
for arg in "$@"; do
    case $arg in
        -h | --help)
            show_help
            exit 0
            ;;
        -v | --verbose)
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

# HELPERS

log() {
    if [ "$VERBOSE" = true ]; then
        echo "$@"
    fi
}

bail_on_error() {
    # $1 : exit status of command
    # $2 : error message

    if [ "$1" -ne 0 ]; then
        log "❌ Error: $2 (exit code: $1)"
        exit "$1"
    fi
}

# PLATFORM SPECIFICS

VENV_DIR=".venv"

case "$(uname -s)" in
    *MINGW* | *MSYS* | *CYGWIN*)
        VENV_BIN="$VENV_DIR/Scripts"
        ;;
    *)
        VENV_BIN="$VENV_DIR/bin"
        ;;
esac

VENV_PIP="$VENV_BIN/pip"
PYTHON="python3"

# MAIN

if [ ! -d "$VENV_DIR" ]; then
    log "🐍 Creating Python venv in '$VENV_DIR'..."
    $PYTHON -m venv $VENV_DIR
fi

log "🔧 [pip] Installing project and dependencies..."

"$VENV_PIP" install $PIP_FLAGS -e .
bail_on_error $? "[pip] Failed to install project and dependencies."

FLEXY_PATH="$VENV_BIN/flexy"

log "🔧 [flexy] Running setup..."
"$FLEXY_PATH" setup $APP_FLAGS
bail_on_error $? "[flexy] Setup failed."

log "🔧 [flexy] Running install..."
"$FLEXY_PATH" install $APP_FLAGS
bail_on_error $? "[flexy] Install failed."

log "✅ Bootstrap complete."
