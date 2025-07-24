from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('This is a help message. Here you can find information about available commands.')

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
    
    await update.message.reply_text(
        f'I received your location! Latitude: {latitude}, Longitude: {longitude}\n'
        f'I will use this information to find services near you.'
    )

def main():
    app = ApplicationBuilder().token("8232641420:AAE7QwpDl2xHMVeiZpe3MHtQO5LeAdwpEF4").build()

    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    print("Starting up application...")
    
    app.run_polling()

if __name__ == "__main__":
    main()