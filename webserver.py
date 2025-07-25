from fastapi import FastAPI, Request, BackgroundTasks
from telegram import Update
from telegram_bot import create_bot_app
import os
import logging
import asyncio
import aiohttp
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
bot_app = None

async def keep_alive():
    """Keep the service alive by making periodic requests"""
    while True:
        try:
            await asyncio.sleep(840)  # Wait 14 minutes (840 seconds)
            async with aiohttp.ClientSession() as session:
                async with session.get("https://ms-finder-tele-bot.onrender.com/health") as response:
                    logger.info(f"Keep-alive ping: {response.status} at {datetime.now()}")
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize bot and set webhook on startup"""
    global bot_app
    bot_app = create_bot_app()
    
    if bot_app:
        try:
            # Initialize the application
            await bot_app.initialize()
            logger.info("Bot application initialized successfully")
            
            # Get the webhook URL
            webhook_url = os.getenv("WEBHOOK_URL")
            if not webhook_url:
                webhook_url = "https://ms-finder-tele-bot.onrender.com/webhook"
                logger.info(f"Using service webhook URL: {webhook_url}")
            
            # Set webhook
            await bot_app.bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set successfully to: {webhook_url}")
            
            # Start keep-alive task
            asyncio.create_task(keep_alive())
            logger.info("Keep-alive task started")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot or set webhook: {e}")
    else:
        logger.error("Failed to create bot app")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    global bot_app
    if bot_app:
        try:
            await bot_app.shutdown()
            logger.info("Bot application shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhook updates from Telegram"""
    try:
        if bot_app:
            update_data = await request.json()
            update = Update.de_json(update_data, bot_app.bot)
            
            # Process the update using the application's update queue
            await bot_app.update_queue.put(update)
            
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Musollah Finder Bot is running!", 
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "bot_initialized": bot_app is not None,
        "timestamp": datetime.now().isoformat()
    }

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

@app.get("/ping")
async def ping():
    """Simple ping endpoint for keep-alive"""
    return {"ping": "pong", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)