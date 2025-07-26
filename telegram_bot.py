import os
import requests
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from geopy.distance import geodesic
from datetime import datetime
from sheets_service import fetch_locations
from constants import CMD_HELLO, CMD_START, CMD_HELP, CMD_LOCATION
import psycopg2
from psycopg2.extras import execute_values
from database_service import init_database, log_user_to_postgres

load_dotenv()

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    log_user_to_postgres(user)
    await update.message.reply_text(
        "🕌 Ready to help you find prayer spaces!\n\n"
        "📍 Send your location to get started:\n"
        "• Tap the attachment icon (📎)\n"
        "• Select \"Location\"\n"
        "• Share your current location\n\n"
        "I'll find the nearest musollah with directions! 🧭"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'To find the nearest musollah 🕌:\n\n'
        f'Tap the attachment icon (paperclip), select "Location", and send your current location 📍.'
    )

def get_nearest_musollah(update, lat, lon):
    # Fetch locations from Google Sheets
    locations = fetch_locations()
    
    # If no locations are found, inform the user
    if not locations:
        return update.message.reply_text(
            "Sorry, I couldn't retrieve the musollah locations at the moment. Please try again later.",
            parse_mode=constants.ParseMode.HTML
        )
    
    # Find the closest musollah
    closest = min(
        locations,
        key=lambda loc: geodesic((lat, lon), (loc["lat"], loc["lon"])).kilometers
    )
    distance = geodesic((lat, lon), (closest["lat"], closest["lon"])).kilometers
    
    # Use the Google Maps link from the data if available, otherwise construct it
    if "google_maps" in closest and closest["google_maps"]:
        gmaps_link = closest["google_maps"]
    else:
        gmaps_link = f'https://www.google.com/maps/search/?api=1&destination={closest["name"].replace(" ", "+")}@{closest["lat"]},{closest["lon"]}'

    navigate_text = f'<b>Navigate:</b> <a href="{gmaps_link}">Open in Google Maps</a>' if gmaps_link else ''

    details = closest.get("details")
    details_text = f'<b>Additional Info:</b>\n{details}\n\n' if details else ''

    return update.message.reply_text(
        f'<b>{closest["name"]}</b>\n'
        f'<b>Distance:</b> {distance:.2f} kilometers\n\n'
        f'<b>Directions:</b>\n{closest["directions"]}\n\n'
        f'{details_text}'
        f'{navigate_text}',
        parse_mode=constants.ParseMode.HTML
    )

async def location_pindrop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
    await get_nearest_musollah(update, latitude, longitude)

async def location_postal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or len(context.args[0]) != 6 or not context.args[0].isdigit():
        await update.message.reply_text(f"Please provide a valid 6-digit Singapore postal code. Example: /{CMD_LOCATION} 119077")
        return

    postal_code = context.args[0]
    url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=N"
    try:
        response = requests.get(url)
        data = response.json()
        results = data.get('results', [])
        if not results:
            await update.message.reply_text("Postal code not found. Please check and try again.")
            return
        lat = float(results[0]['LATITUDE'])
        lon = float(results[0]['LONGITUDE'])
    except Exception as e:
        await update.message.reply_text("Error looking up postal code. Please try again later.")
        return

    await get_nearest_musollah(update, lat, lon)

def create_bot_app():
    environment = os.getenv("ENVIRONMENT", "dev").lower()
    
    if environment == "prod":
        token = os.getenv("TELEGRAM_BOT_TOKEN_PROD")
    else:
        token = os.getenv("TELEGRAM_BOT_TOKEN_DEV")
    
    if not token:
        print(f"Error: TELEGRAM_BOT_TOKEN_{environment.upper()} environment variable not set.")
        return None

    app = ApplicationBuilder().token(token).build()

    init_database()

    app.add_handler(CommandHandler(CMD_HELLO, hello))
    app.add_handler(CommandHandler(CMD_START, start_command))
    app.add_handler(CommandHandler(CMD_HELP, help_command))
    app.add_handler(CommandHandler(CMD_LOCATION, location_postal_handler))
    app.add_handler(MessageHandler(filters.LOCATION, location_pindrop_handler))

    return app

# For local testing only
if __name__ == "__main__":
    bot_app = create_bot_app()
    if bot_app:
        print(f"Bot running at {datetime.now()}...")
        try:
            bot_app.run_polling()
        except KeyboardInterrupt:
            print("Bot stopped.")
    else:
        print("Failed to create bot app... Check environment variables and code logic.")