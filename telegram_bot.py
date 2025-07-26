import os
import requests
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from geopy.distance import geodesic
from datetime import datetime
from location_service import fetch_all_locations
from constants import CMD_HELLO, CMD_START, CMD_HELP, CMD_LOCATION, CMD_NEAREST

load_dotenv()

# Conversation states
WAITING_FOR_LOCATION = 1

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🕌 Ready to help you find prayer spaces!\n\n"
        "📍 Send your location to get started:\n"
        "• Tap the attachment icon (📎)\n"
        "• Select \"Location\"\n"
        "• Share your current location\n\n"
        "I'll find the nearest musollah with directions! 🧭\n\n"
        "💡 <b>Pro tip:</b> Use /{} followed by a number (e.g., /{} 3) to find multiple nearby prayer spaces.".format(CMD_NEAREST, CMD_NEAREST),
        parse_mode=constants.ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'To find the nearest musollah 🕌:\n\n'
        f'Tap the attachment icon (paperclip), select "Location", and send your current location 📍.\n\n\n'
        f'<b>Available Commands:</b>\n\n'
        f'/{CMD_START} - Start the bot\n'
        f'/{CMD_HELLO} - Get a greeting\n'
        f'/{CMD_HELP} - Show this help message\n'
        f'/{CMD_LOCATION} [postal_code] - Find nearest prayer space using a postal code\n'
        f'/{CMD_NEAREST} [number] - Find multiple nearest prayer spaces\n\n'
        f'<b>How to use:</b>\n'
        f'• To find the nearest prayer space, tap the attachment icon (📎), select "Location", and share your current location.\n\n'
        f'• To find multiple nearby prayer spaces, use /{CMD_NEAREST} followed by a number (e.g., /{CMD_NEAREST} 3). Maximum 5 locations can be shown.\n\n'
        f'• To cancel any ongoing command, type /cancel.',
        parse_mode=constants.ParseMode.HTML
    )

def get_nearest_musollah(update, lat, lon, count=1):
    # Fetch locations from all sources (Google Sheets and API)
    locations = fetch_all_locations()
    
    # If no locations are found, inform the user
    if not locations:
        return update.message.reply_text(
            "Sorry, I couldn't retrieve the musollah locations at the moment. Please try again later.",
            parse_mode=constants.ParseMode.HTML
        )
    
    # Calculate distances for all locations
    for location in locations:
        location['distance'] = geodesic((lat, lon), (location["lat"], location["lon"])).kilometers
    
    # Sort locations by distance
    sorted_locations = sorted(locations, key=lambda loc: loc['distance'])
    
    # Limit to the requested number of locations
    nearest_locations = sorted_locations[:count]
    
    if count == 1:
        # Single location response (original behavior)
        closest = nearest_locations[0]
        distance = closest['distance']
        
        # Use the Google Maps link from the data if available, otherwise construct it
        if "google_maps" in closest and closest["google_maps"]:
            gmaps_link = closest["google_maps"]
        else:
            gmaps_link = f'https://www.google.com/maps/search/?api=1&query={closest["lat"]},{closest["lon"]}'
        
        # Safely get directions and details, providing defaults if missing
        directions = closest.get("directions", "No directions available")
        details = closest.get("details", "No additional information available")
        
        return update.message.reply_text(
            f'<b>{closest["name"]}</b>\n'
            f'<b>Distance:</b> {distance:.2f} kilometers\n\n'
            f'<b>Directions:</b>\n{directions}\n\n'
            f'<b>Additional Info:</b>\n{details}\n\n'
            f'<b>View on Map:</b> <a href="{gmaps_link}">Open in Google Maps</a>',
            parse_mode=constants.ParseMode.HTML
        )
    else:
        # Multiple locations response
        response_text = f'<b>🕌 {count} Nearest Prayer Spaces:</b>\n\n'
        
        for i, location in enumerate(nearest_locations, 1):
            # Use the Google Maps link from the data if available, otherwise construct it
            if "google_maps" in location and location["google_maps"]:
                gmaps_link = location["google_maps"]
            else:
                gmaps_link = f'https://www.google.com/maps/search/?api=1&query={location["lat"]},{location["lon"]}'
            
            # Safely get directions and details, providing defaults if missing
            directions = location.get("directions", "No directions available")
            details = location.get("details", "No additional information available")
            
            response_text += (
                f'<b>{i}. {location["name"]}</b>\n'
                f'<b>Distance:</b> {location["distance"]:.2f} kilometers\n\n'
                f'<b>Directions:</b>\n{directions}\n\n'
                f'<b>Additional Info:</b>\n{details}\n\n'
                f'<b>View on Map:</b> <a href="{gmaps_link}">Open in Google Maps</a>\n\n\n'
            )
        
        return update.message.reply_text(
            response_text,
            parse_mode=constants.ParseMode.HTML
        )

async def location_pindrop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
    
    # Check if this is part of a /nearest conversation
    if 'nearest_count' in context.user_data:
        count = context.user_data['nearest_count']
        del context.user_data['nearest_count']  # Clear the data after use
        await get_nearest_musollah(update, latitude, longitude, count)
        return ConversationHandler.END
    else:
        # Regular location handling
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

    # Check if this is part of a /nearest conversation
    if 'nearest_count' in context.user_data:
        count = context.user_data['nearest_count']
        del context.user_data['nearest_count']  # Clear the data after use
        await get_nearest_musollah(update, lat, lon, count)
        return ConversationHandler.END
    else:
        # Regular location handling
        await get_nearest_musollah(update, lat, lon)

async def nearest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Check if a number was provided
    if not context.args:
        await update.message.reply_text(
            "Please specify how many nearest locations you want to see.\n"
            "Example: /nearest 3"
        )
        return ConversationHandler.END
    
    try:
        count = int(context.args[0])
        if count < 1:
            raise ValueError("Count must be positive")
        if count > 5:  # Limit to 5 to avoid overly long messages
            count = 5
            await update.message.reply_text("Maximum 5 locations can be shown. I'll show you the 5 nearest locations.")
    except ValueError:
        await update.message.reply_text(
            "Please provide a valid number.\n"
            "Example: /nearest 3"
        )
        return ConversationHandler.END
    
    # Store the count in user data
    context.user_data['nearest_count'] = count
    
    await update.message.reply_text(
        f"I'll show you the {count} nearest prayer spaces.\n\n"
        f"Please share your location by:\n"
        f"• Tapping the attachment icon (📎)\n"
        f"• Selecting 'Location'\n"
        f"• Sharing your current location\n\n"
        f"Or send a Singapore postal code."
    )
    
    return WAITING_FOR_LOCATION

async def cancel_nearest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Clear the stored count
    if 'nearest_count' in context.user_data:
        del context.user_data['nearest_count']
    
    await update.message.reply_text("Command cancelled.")
    return ConversationHandler.END

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

    # Regular command handlers
    app.add_handler(CommandHandler(CMD_HELLO, hello))
    app.add_handler(CommandHandler(CMD_START, start_command))
    app.add_handler(CommandHandler(CMD_HELP, help_command))
    app.add_handler(CommandHandler(CMD_LOCATION, location_postal_handler))
    
    # Conversation handler for /nearest command
    nearest_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(CMD_NEAREST, nearest_command)],
        states={
            WAITING_FOR_LOCATION: [
                MessageHandler(filters.LOCATION, location_pindrop_handler),
                CommandHandler(CMD_LOCATION, location_postal_handler)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_nearest)],
    )
    app.add_handler(nearest_conv_handler)
    
    # Regular location handler (for direct location sharing)
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