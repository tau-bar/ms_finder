from fastapi import FastAPI, Request
from telegram import Update
from telegram_bot import create_bot_app
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
bot_app = None

@app.on_event("startup")
async def startup_event():
    """Initialize bot and set webhook on startup"""
    global bot_app
    bot_app = create_bot_app()
    
    if bot_app:
        # Get the webhook URL from environment variable or use the service URL
        webhook_url = os.getenv("WEBHOOK_URL")
        if not webhook_url:
            # Use your actual Render service URL
            webhook_url = "https://ms-finder-tele-bot.onrender.com/webhook"
            logger.info(f"Using service webhook URL: {webhook_url}")
        
        try:
            # Set webhook
            await bot_app.bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set successfully to: {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    else:
        logger.error("Failed to create bot app")

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhook updates from Telegram"""
    try:
        if bot_app:
            update_data = await request.json()
            update = Update.de_json(update_data, bot_app.bot)
            
            # Process the update
            await bot_app.process_update(update)
            
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "Musollah Finder Bot is running!", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/webhook-info")
async def webhook_info():
    """Get current webhook information"""
    if bot_app:
        try:
            webhook_info = await bot_app.bot.get_webhook_info()
            return {
                "webhook_url": webhook_info.url,
                "has_custom_certificate": webhook_info.has_custom_certificate,
                "pending_update_count": webhook_info.pending_update_count,
                "last_error_date": webhook_info.last_error_date,
                "last_error_message": webhook_info.last_error_message,
                "max_connections": webhook_info.max_connections,
                "allowed_updates": webhook_info.allowed_updates
            }
        except Exception as e:
            return {"error": str(e)}
    return {"error": "Bot not initialized"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)