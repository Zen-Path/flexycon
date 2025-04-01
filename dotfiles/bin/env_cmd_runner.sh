#!/bin/bash

# Check if at least one argument (the command) is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <command> <file1> [file2] ..."
    exit 1
fi

# The first argument is the command (e.g., zathura, or $EDITOR)
COMMAND=$1

# Check if the command is an environment variable (like $EDITOR)
if [[ "$COMMAND" == "\$"* ]]; then
    # Remove the leading "$"
    VAR_NAME=${COMMAND:1}
    COMMAND_EXPANDED="${!VAR_NAME}"
else
    COMMAND_EXPANDED="$COMMAND"
fi

if [ -z "$COMMAND_EXPANDED" ]; then
    echo "Error: The command $COMMAND could not be expanded."
    exit 1
fi

# Remove the first argument so $@ now contains the list of files
shift

# Check if the script is running in a terminal or not
if [ "$(tty)" = "not a tty" ]; then
    # If not a tty, launch a terminal and run the command with the files
    $TERMINAL -e $COMMAND_EXPANDED "$@"
else
    # If running in a terminal, directly run the command with the files
    $COMMAND_EXPANDED "$@"
fi
