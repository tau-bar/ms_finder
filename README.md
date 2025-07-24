# Telegram Bot

## Setup

### Option 1: Using the setup script (recommended)

1. Make sure you have Python 3.9 or newer installed
2. Create a new bot and get a token from [@BotFather](https://t.me/BotFather) on Telegram
3. Replace `YOUR_TOKEN` in the `telegram_bot.py` file with your actual bot token
4. Make the setup script executable and run it:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```
5. Run the bot using the run script:
   ```
   chmod +x run_bot.sh
   ./run_bot.sh
   ```
   
   Or run it directly:
   ```
   python3 telegram_bot.py
   ```

### Option 2: Manual setup

1. Make sure you have Python 3.9 or newer installed
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required libraries using the requirements.txt file:
   ```
   pip install -r requirements.txt
   ```
4. Create a new bot and get a token from [@BotFather](https://t.me/BotFather) on Telegram
5. Replace `YOUR_TOKEN` in the `telegram_bot.py` file with your actual bot token
6. Run the bot:
   ```
   python telegram_bot.py
   ```

## Dependencies

This bot requires the following dependencies:

- `python-telegram-bot` (v22.3): The main library for Telegram bot functionality
- `pytz`: Required for timezone handling with the APScheduler component used by python-telegram-bot

All dependencies are listed in the `requirements.txt` file.