from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from telegram_bot import create_bot_app

bot_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global bot_task
    bot_app = create_bot_app()
    if bot_app:
        # Start the bot in the background
        bot_task = asyncio.create_task(bot_app.run_polling())
        print("Telegram bot started!")
    
    yield
    
    # Shutdown
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
        print("Telegram bot stopped!")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Musollah Finder Bot is running!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)