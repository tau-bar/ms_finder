import os
import requests
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from geopy.distance import geodesic
from datetime import datetime
import pytz

from database_service import init_database, log_user_to_supabase
from location_service import fetch_all_locations
from constants import CMD_HELLO, CMD_START, CMD_HELP, CMD_LOCATION, CMD_NEAREST, CMD_FEEDBACK

load_dotenv()

# Conversation states
WAITING_FOR_COUNT = 1
WAITING_FOR_LOCATION = 2
WAITING_FOR_FEEDBACK = 3

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    log_user_to_supabase(user)
    await update.message.reply_text(
        "🕌 Ready to help you find prayer spaces!\n\n"
        "📍 Send your location to get started:\n"
        "• Tap the attachment icon (📎)\n"
        "• Select \"Location\"\n"
        "• Share your current location\n\n"
        "I'll find the nearest musollah(s) with directions! 🧭\n\n"
        "💡 <b>Pro tip:</b> For better accuracy, enable <b>precise location</b> in your phone settings.",
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
        f'/{CMD_LOCATION} - Find nearest prayer space using a postal code\n'
        f'/{CMD_NEAREST} - Find multiple nearest prayer spaces\n'
        f'/{CMD_FEEDBACK} - Send feedback to the developers\n\n'
        "💡 <b>Pro tip:</b> For better accuracy, enable <b>precise location</b> in your phone settings.\n\n"
        f'<b>How to use:</b>\n\n'
        f'• To find the nearest prayer space, tap the attachment icon (📎), select "Location", and share your current location.\n\n'
        f'• To find the nearest prayer space using a postal code, use /{CMD_LOCATION} and follow the prompts to enter a 6-digit Singapore postal code.\n\n'
        f'• To find multiple nearby prayer spaces, use /{CMD_NEAREST} and follow the prompts to specify how many locations you want to see (maximum 5).\n\n'
        f'• To send feedback, use /{CMD_FEEDBACK} and follow the prompts to submit your message.\n\n'
        f'• To cancel any ongoing command, type /cancel.',
        parse_mode=constants.ParseMode.HTML
    )

def _get_gmaps_link(location):
    """Extract or generate Google Maps link from location data."""
    if "google_maps" in location and location["google_maps"]:
        return location["google_maps"]
    elif "lat" in location and "lon" in location:
        return f"https://www.google.com/maps/search/?api=1&query={location['lat']},{location['lon']}"
    return ''

def _format_location_details(location, index=None):
    """Format the details of a location for display.
    
    Args:
        location: The location data dictionary
        index: Optional index for numbered lists (used in multiple locations display)
        
    Returns:
        Formatted location details as HTML text
    """
    # Basic location information
    name_prefix = f"{index}. " if index is not None else ""
    name = f'<b>{name_prefix}{location["name"]}</b>\n'
    if (not location["type"] or location["type"].lower() == "musollah") and "musollah" not in location["name"].lower():
        name = f'<b>{name_prefix}{location["name"]} Musollah</b>\n'
    
    # Address and Google Maps link
    gmaps_link = _get_gmaps_link(location)
    address_line = ""
    if "address" in location and location["address"]:
        if gmaps_link:
            address_line = f'<b>Address:</b> {location["address"]} (<a href="{gmaps_link}">Google Maps</a>)\n'
        else:
            address_line = f'<b>Address:</b> {location["address"]}\n'
    elif gmaps_link:
        address_line = f'<b>Address:</b> <a href="{gmaps_link}">Google Maps</a>\n'
    
    # Distance
    distance_line = f'<b>Distance:</b> {location["distance"]:.2f} kilometers\n'
    
    # Directions (only if video guide is available)
    video_guide = location.get("guide", "")
    directions_line = ""
    if video_guide:
        directions_line = f'<b>Directions:</b> <a href="{video_guide}">Directional Video</a>\n'
    elif location.get("directions"):
        directions_line = f'<b>Directions:</b> {location.get("directions")}\n'
    
    # Additional details
    details = location.get("details", "")
    details_lines = f'<b>Additional Info:</b> {details}' if details and details.strip() else ""
    
    return name + address_line + distance_line + directions_line + details_lines

def get_nearest_musollah_text(lat, lon, count=1):
    # Fetch locations from all sources (Google Sheets and API)
    locations = fetch_all_locations()
    
    # If no locations are found, inform the user
    if not locations:
        return (
            "Sorry, I couldn't retrieve the musollah locations at the moment. Please try again later."
        )
    
    # Calculate distances for all locations
    for location in locations:
        location['distance'] = geodesic((lat, lon), (location["lat"], location["lon"])).kilometers
    
    # Sort locations by distance
    sorted_locations = sorted(locations, key=lambda loc: loc['distance'])
    
    # Limit to the requested number of locations
    nearest_locations = sorted_locations[:count]
    
    if count == 1:
        # Single location response
        return _format_location_details(nearest_locations[0])
    else:
        # Multiple locations response
        response_text = f'<b>🕌 {count} Nearest Prayer Spaces:</b>\n\n'
        
        for i, location in enumerate(nearest_locations, 1):
            response_text += _format_location_details(location, i)
            if i < len(nearest_locations):  # Add separator between locations except after the last one
                response_text += "\n\n"
        
        return response_text

async def location_pindrop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    loading_msg = await update.message.reply_text("Finding the nearest musollah...⏳")
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
    
    # Check if this is part of a /nearest conversation
    if 'nearest_count' in context.user_data:
        count = context.user_data['nearest_count']
        del context.user_data['nearest_count']  # Clear the data after use
        final_text = get_nearest_musollah_text(latitude, longitude, count)
        await loading_msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)
        return ConversationHandler.END
    else:
        # Regular location handling
        final_text = get_nearest_musollah_text(latitude, longitude)
        await loading_msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)

async def location_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation flow for the /location command."""
    user = update.effective_user
    log_user_to_supabase(user)
    
    await update.message.reply_text(
        "📍 Please send me a 6-digit Singapore postal code to find the nearest prayer space.\n\n"
        "Example: 119077\n\n"
        "You can cancel anytime by typing /cancel."
    )
    
    return WAITING_FOR_LOCATION

async def process_postal_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the postal code sent by the user."""
    loading_msg = await update.message.reply_text("Finding the nearest musollah...⏳")
    postal_code = update.message.text.strip()
    
    if len(postal_code) != 6 or not postal_code.isdigit():
        await loading_msg.edit_text("Please provide a valid 6-digit Singapore postal code. Example: 119077")
        return WAITING_FOR_LOCATION

    url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=N"
    try:
        response = requests.get(url)
        data = response.json()
        results = data.get('results', [])
        if not results:
            await loading_msg.edit_text("Postal code not found. Please check and try again.")
            return WAITING_FOR_LOCATION
        lat = float(results[0]['LATITUDE'])
        lon = float(results[0]['LONGITUDE'])
    except Exception as e:
        await loading_msg.edit_text("Error looking up postal code. Please try again later.")
        return WAITING_FOR_LOCATION

    # Check if this is part of a /nearest conversation
    if 'nearest_count' in context.user_data:
        count = context.user_data['nearest_count']
        del context.user_data['nearest_count']  # Clear the data after use
        final_text = get_nearest_musollah_text(lat, lon, count)
        await loading_msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)
    else:
        # Regular location handling
        final_text = get_nearest_musollah_text(lat, lon)
        await loading_msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)
    
    return ConversationHandler.END

async def cancel_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the location conversation."""
    await update.message.reply_text("Command cancelled.")
    return ConversationHandler.END

async def nearest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation flow for the /nearest command."""
    user = update.effective_user
    log_user_to_supabase(user)
    
    await update.message.reply_text(
        "🔍 How many nearest prayer spaces would you like to see? (maximum 5)\n\n"
        "Please enter a number between 1 and 5.\n\n"
        "You can cancel anytime by typing /cancel."
    )
    
    return WAITING_FOR_COUNT

async def process_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the count number sent by the user."""
    try:
        count = int(update.message.text.strip())
        if count < 1:
            await update.message.reply_text("Please provide a positive number.")
            return WAITING_FOR_COUNT
        if count > 5:  # Limit to 5 to avoid overly long messages
            count = 5
            await update.message.reply_text("Maximum 5 locations can be shown. I'll show you the 5 nearest locations.")
    except ValueError:
        await update.message.reply_text(
            "Please provide a valid number between 1 and 5."
        )
        return WAITING_FOR_COUNT
    
    # Store the count in user data
    context.user_data['nearest_count'] = count
    
    await update.message.reply_text(
        f"I'll show you the {count} nearest prayer spaces.\n\n"
        f"Please share your location by:\n"
        f"• Tapping the attachment icon (📎)\n"
        f"• Selecting 'Location'\n"
        f"• Sharing your current location\n\n"
        f"Or send a 6-digit Singapore postal code.\n\n"
        f"You can cancel anytime by typing /cancel."
    )
    
    return WAITING_FOR_LOCATION

async def cancel_nearest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Clear the stored count
    if 'nearest_count' in context.user_data:
        del context.user_data['nearest_count']
    
    await update.message.reply_text("Command cancelled.")
    return ConversationHandler.END

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the /feedback command to start the feedback conversation flow."""
    user = update.effective_user
    log_user_to_supabase(user)
    
    await update.message.reply_text(
        "📝 We'd love to hear your feedback! Please type your message below.\n\n"
        "You can cancel anytime by typing /cancel."
    )
    
    return WAITING_FOR_FEEDBACK

async def process_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the feedback message sent by the user."""
    user = update.effective_user
    message_text = update.message.text
    
    # Format the feedback message with user info and timestamp
    singapore_tz = pytz.timezone('Asia/Singapore')  # GMT+8 timezone
    current_time = datetime.now(singapore_tz).strftime("%H:%M %d/%m/%Y")
    feedback_formatted = (
        f"📩 <b>New Feedback</b>\n\n"
        f"<b>From:</b> {user.first_name} {user.last_name if user.last_name else ''}\n"
        f"<b>Username:</b> @{user.username if user.username else 'None'}\n"
        f"<b>User ID:</b> {user.id}\n"
        f"<b>Time:</b> {current_time}\n\n"
        f"<b>Message:</b>\n{message_text}"
    )
    
    # Get the developer group chat ID from environment variables
    developer_group_id = os.getenv("DEVELOPER_GROUP_ID")
    
    if developer_group_id:
        try:
            # Forward the feedback to the developer group
            await context.bot.send_message(
                chat_id=developer_group_id,
                text=feedback_formatted,
                parse_mode=constants.ParseMode.HTML
            )
            
            # Confirm to the user that feedback was sent
            await update.message.reply_text(
                "Thank you for your feedback! It has been sent to our development team."
            )
        except Exception as e:
            print(f"Error sending feedback to developer group: {e}")
            await update.message.reply_text(
                "Sorry, there was an error sending your feedback. Please try again later."
            )
    else:
        print("DEVELOPER_GROUP_ID not set in environment variables")
        # Still thank the user even if we couldn't forward it (for better UX)
        await update.message.reply_text(
            "Thank you for your feedback! Our team will review it soon."
        )
    
    return ConversationHandler.END

async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the feedback conversation."""
    await update.message.reply_text("Feedback cancelled.")
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

    init_database()

    # Regular command handlers
    app.add_handler(CommandHandler(CMD_HELLO, hello))
    app.add_handler(CommandHandler(CMD_START, start_command))
    app.add_handler(CommandHandler(CMD_HELP, help_command))
    
    # Conversation handler for /location command
    location_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(CMD_LOCATION, location_command)],
        states={
            WAITING_FOR_LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_postal_code)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_location)],
    )
    app.add_handler(location_conv_handler)
    
    # Conversation handler for /nearest command
    nearest_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(CMD_NEAREST, nearest_command)],
        states={
            WAITING_FOR_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_count)
            ],
            WAITING_FOR_LOCATION: [
                MessageHandler(filters.LOCATION, location_pindrop_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_postal_code)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_nearest)],
    )
    app.add_handler(nearest_conv_handler)
    
    # Conversation handler for /feedback command
    feedback_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(CMD_FEEDBACK, feedback_command)],
        states={
            WAITING_FOR_FEEDBACK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_feedback)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_feedback)],
    )
    app.add_handler(feedback_conv_handler)
    
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