from fastapi import FastAPI, Request
from telegram import Update
from telegram_bot import create_bot_app
import os
import logging
import asyncio
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
bot_app = None

load_dotenv()
PROD_URL = os.getenv("PROD_URL")

async def keep_alive():
    """Keep the service alive by making periodic requests"""
    while True:
        try:
            await asyncio.sleep(840)  # Wait 14 minutes
            async with aiohttp.ClientSession() as session:
                async with session.get(PROD_URL + "health") as response:
                    logger.info(f"Keep-alive ping: {response.status} at {datetime.now()}")
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize bot and set webhook on startup"""
    global bot_app
    
    try:
        bot_app = create_bot_app()
        
        if bot_app:
            await bot_app.initialize()
            await bot_app.start()
            
            logger.info("Bot application initialized and started successfully")
            
            webhook_url = os.getenv(PROD_URL + "webhook")
            logger.info(f"Using webhook URL: {webhook_url}")
            
            await bot_app.bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set successfully")
            
            webhook_info = await bot_app.bot.get_webhook_info()
            logger.info(f"Webhook verification - URL: {webhook_info.url}, Pending: {webhook_info.pending_update_count}")
            
            asyncio.create_task(keep_alive())
            logger.info("Keep-alive task started")
            
        else:
            logger.error("Failed to create bot app")
            
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    global bot_app
    if bot_app:
        try:
            await bot_app.stop()
            await bot_app.shutdown()
            logger.info("Bot application stopped and shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhook updates from Telegram"""
    try:
        # Log the incoming request
        update_data = await request.json()
        logger.info(f"Received webhook update: {update_data}")
        
        if bot_app:
            # Create Update object
            update = Update.de_json(update_data, bot_app.bot)
            logger.info(f"Parsed update: {update.update_id}")
            
            try:
                await bot_app.process_update(update)
                logger.info(f"Successfully processed update {update.update_id}")
            except Exception as process_error:
                logger.error(f"Error processing update {update.update_id}: {process_error}", exc_info=True)
            
        else:
            logger.error("Bot app not initialized")
            
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Musollah Finder Bot is running!", 
        "status": "active",
        "bot_ready": bot_app is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    bot_status = "ready" if bot_app else "not_initialized"
    return {
        "status": "ok", 
        "bot_status": bot_status,
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
                "last_error_date": webhook_info.last_error_date.isoformat() if webhook_info.last_error_date else None,
                "last_error_message": webhook_info.last_error_message,
                "max_connections": webhook_info.max_connections,
                "allowed_updates": webhook_info.allowed_updates,
                "ip_address": webhook_info.ip_address
            }
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
            return {"error": str(e)}
    return {"error": "Bot not initialized"}

@app.get("/test-bot")
async def test_bot():
    """Test endpoint to check bot functionality"""
    if bot_app:
        try:
            me = await bot_app.bot.get_me()
            return {
                "bot_username": me.username,
                "bot_name": me.first_name,
                "bot_id": me.id,
                "can_join_groups": me.can_join_groups,
                "can_read_all_group_messages": me.can_read_all_group_messages,
                "supports_inline_queries": me.supports_inline_queries
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