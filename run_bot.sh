#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please run setup.sh first or create a .env file with your TELEGRAM_BOT_TOKEN."
    exit 1
fi

# Run the bot with auto-restart on code changes
watchmedo auto-restart --patterns="*.py" --recursive -- python3 telegram_bot.py