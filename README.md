# Telegram Bot

## Setup

### Option 1: Using the setup script (recommended)

1. Make sure you have Python 3.9 or newer installed
2. Create a new bot and get a token from [@BotFather](https://t.me/BotFather) on Telegram
3. Create a `.env` file in the project root directory with your bot token (you can use the provided `.env.example` as a template):
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
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
5. Create a `.env` file in the project root directory with your bot token (you can use the provided `.env.example` as a template):
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
6. Run the bot:
   ```
   python telegram_bot.py
   ```

## Features

### Commands
- `/hello`: Greets the user with their first name
- `/start`: Displays a welcome message and instructions
- `/help`: Displays help information about available commands
- `/location <postal_code>`: Finds the nearest prayer space using a Singapore postal code
- `/nearest <number>`: Finds multiple nearest prayer spaces (up to 5)

### Location Sharing
The bot can receive location data shared by users and find the closest predefined locations from its database. When a user shares their location, the bot will:
1. Calculate the distance to each predefined location
2. Identify the closest location(s)
3. Respond with details including name, distance, directions, and a Google Maps link

#### Finding Multiple Nearby Locations
Users can find multiple nearby prayer spaces using the `/nearest` command:
1. Send `/nearest` followed by a number (e.g., `/nearest 3`) - maximum 5 locations can be shown
2. Share your location when prompted
3. The bot will respond with the specified number of nearest locations, sorted by distance

### Location Data Sources

#### Google Sheets Integration
The bot retrieves location data from a Google Sheets spreadsheet. This allows for easier management and updating of location data without modifying the code.

To set up the Google Sheets integration:
1. Follow the instructions in the `GOOGLE_SHEETS_SETUP.md` file
2. Create a public spreadsheet with columns for Name, Latitude, Longitude, Directions, Details, and Google Maps link
3. Update your `.env` file with your Google Sheets API key and spreadsheet ID

#### Musollah API Integration
The bot also fetches location data from the Musollah API, providing additional prayer spaces beyond those in your spreadsheet.

To set up the Musollah API integration:
1. Obtain an API key for the Musollah API
2. Add the API key to your `.env` file as `MUSOLLAH_API_KEY=your_key_here`

## Dependencies

This bot requires the following dependencies:

- `python-telegram-bot` (v22.3): The main library for Telegram bot functionality
- `pytz`: Required for timezone handling with the APScheduler component used by python-telegram-bot
- `geopy`: Used for calculating distances between geographical coordinates
- `python-dotenv`: Used for loading environment variables from a .env file
- `google-api-python-client`: Used for Google Sheets API integration with API key authentication
- `requests`: Used for making HTTP requests to the Musollah API

All dependencies are listed in the `requirements.txt` file.