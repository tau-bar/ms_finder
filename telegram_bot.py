import os
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from geopy.distance import geodesic
from musollah_locations import locations

# Load environment variables from .env file
load_dotenv()

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
        
    # Find the closest location to the user
    closest = min(
        locations,
        key=lambda loc: geodesic((latitude, longitude), (loc["lat"], loc["lon"])).kilometers
    )
    
    # Calculate the distance
    distance = geodesic((latitude, longitude), (closest["lat"], closest["lon"])).kilometers

    # Google Maps link for navigation
    gmaps_link = f'https://www.google.com/maps/dir/?api=1&destination={closest["lat"]},{closest["lon"]}'

    await update.message.reply_text(
        f'<b>{closest["name"]}</b>\n'
        f'<b>Distance:</b> {distance:.2f} kilometers\n\n'
        f'<b>Directions:</b>\n{closest["directions"]}\n\n'
        f'<b>Additional Info:</b>\n{closest["details"]}\n\n'
        f'<b>Navigate:</b> <a href="{gmaps_link}">Open in Google Maps</a>',
        parse_mode=constants.ParseMode.HTML
    )

def main():
    # Get token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set. Please set it in your .env file.")
        return
        
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    print("Starting up application...")
    
    app.run_polling()

if __name__ == "__main__":
    main()