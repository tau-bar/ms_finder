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

if [ $? -ne 0 ]; then
    echo ""
    echo "Setup encountered issues. Please fix the dependencies before running the bot."
    exit 1
fi

# Check for .env file and create it if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file for bot configuration..."
    echo "Please enter your Telegram Bot Token (from @BotFather):"
    read -r token
    echo "TELEGRAM_BOT_TOKEN_PROD=$token" > .env
    echo ".env file created successfully!"
else
    echo ""
    echo ".env file already exists. If you need to update your token, edit the .env file directly."
fi

echo ""
echo "Setup complete! You can now run the bot with:"
echo "source venv/bin/activate  # If not already activated"
echo "python telegram_bot.py"