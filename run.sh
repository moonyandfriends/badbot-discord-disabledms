#!/bin/bash
# Wrapper script to ensure clean termination for Railway

echo "Starting Discord DM Disabler..."
python main.py
EXIT_CODE=$?

echo "Script completed with exit code: $EXIT_CODE"
echo "Terminating container..."

# Force exit with the script's exit code
exit $EXIT_CODE 