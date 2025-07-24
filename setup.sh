#!/bin/bash

# Setup script for the Telegram Bot

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.9 or newer."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup complete! You can now run the bot with:"
    echo "source venv/bin/activate  # If not already activated"
    echo "python telegram_bot.py"
else
    echo ""
    echo "Setup encountered issues. Please fix the dependencies before running the bot."
    exit 1
fi