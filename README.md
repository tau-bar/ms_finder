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
- `/location`: Starts a conversation to find the nearest prayer space using a Singapore postal code
- `/nearest`: Starts a conversation to find multiple nearest prayer spaces (up to 5)
- `/feedback`: Starts a conversation to collect user feedback

### Location Sharing
The bot can receive location data shared by users and find the closest predefined locations from its database. When a user shares their location, the bot will:
1. Calculate the distance to each predefined location
2. Identify the closest location(s)
3. Respond with details including name, distance, directions, and a Google Maps link

#### Finding the Nearest Prayer Space by Postal Code
Users can find the nearest prayer space using a Singapore postal code with the `/location` command:
1. Send `/location` to start the conversation
2. When prompted, enter a 6-digit Singapore postal code
3. The bot will respond with the nearest prayer space to that postal code

#### Finding Multiple Nearby Locations
Users can find multiple nearby prayer spaces using the `/nearest` command:
1. Send `/nearest` to start the conversation
2. When prompted, enter the number of locations you want to see (maximum 5)
3. Share your location or enter a 6-digit Singapore postal code when prompted
4. The bot will respond with the specified number of nearest locations, sorted by distance

### Location Data Sources

#### Google Sheets Integration
The bot retrieves location data from a Google Sheets spreadsheet. This allows for easier management and updating of location data without modifying the code.

To set up the Google Sheets integration:
1. Follow the instructions in the `GOOGLE_SHEETS_SETUP.md` file
2. Create a public spreadsheet with columns for Name, Latitude, Longitude, Directions, Details, and Google Maps link
3. Update your `.env` file with your Google Sheets API key and spreadsheet ID

#### Musollah API Integration
The bot can fetch location data from the Musollah API, providing additional prayer spaces beyond those in your spreadsheet. This feature is controlled by the `SCOPE` environment variable.

To set up the Musollah API integration:
1. Obtain an API key for the Musollah API
2. Add the API key to your `.env` file as `MUSOLLAH_API_KEY=your_key_here`
3. Set the `SCOPE` environment variable to `sg` in your `.env` file to enable fetching from both Google Sheets and the Musollah API

#### Scope Configuration
The bot supports different scopes for location data sources:

- `SCOPE=nus` (default): Only fetch locations from Google Sheets (NUS-specific locations)
- `SCOPE=sg`: Fetch locations from both Google Sheets and the Musollah API (nationwide coverage)

To configure the scope:
1. Add the `SCOPE` variable to your `.env` file
2. Set it to either `nus` or `sg` based on your needs

### Feedback System

The bot includes a feedback system that allows users to send feedback directly to the developers through a Telegram group.

To set up the feedback system:
1. Create a Telegram group for developers
2. Add your bot to the group
3. Get the group chat ID by adding [@RawDataBot](https://t.me/RawDataBot) to your group temporarily
4. Add the group chat ID to your `.env` file as `DEVELOPER_GROUP_ID=your_group_chat_id_here`

Once configured, users can send feedback using the `/feedback` command, which starts a conversation flow:
1. User sends `/feedback`
2. Bot prompts the user to type their feedback
3. User sends their feedback message
4. Bot confirms receipt and forwards the feedback to the developer group

The forwarded feedback includes the user's name, username, user ID, and timestamp.

## Dependencies

This bot requires the following dependencies:

- `python-telegram-bot` (v22.3): The main library for Telegram bot functionality
- `pytz`: Required for timezone handling with the APScheduler component used by python-telegram-bot
- `geopy`: Used for calculating distances between geographical coordinates
- `python-dotenv`: Used for loading environment variables from a .env file
- `google-api-python-client`: Used for Google Sheets API integration with API key authentication
- `requests`: Used for making HTTP requests to the Musollah API

All dependencies are listed in the `requirements.txt` file.