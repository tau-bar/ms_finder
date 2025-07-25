from fastapi import FastAPI
import asyncio
from telegram_bot import bot_app

app = FastAPI()

@app.on_event("startup")
async def start_bot():
    asyncio.create_task(bot_app.run_polling())
    print("Telegram bot started!")

@app.get("/health")
async def health():
    return {"status": "ok"}
