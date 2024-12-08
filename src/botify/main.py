from .app import create_app
from fastapi import FastAPI
import uvicorn
import asyncio
import signal

# Create the FastAPI app
fastapi_app = FastAPI()

@fastapi_app.get("/test")
async def root():
    return {"message": "Hello World"}

# Create the Telegram bot application
bot_app = create_app()

async def main():
    # Create uvicorn config and server
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    
    # Signal handler for graceful shutdown
    def signal_handler():
        server.should_exit = True
    
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    async with bot_app:
        await bot_app.start()
        await bot_app.updater.start_polling()
        
        # Run the server
        await server.serve()
        
        # When server stops, cleanup the bot
        await bot_app.updater.stop()
        await bot_app.stop()

if __name__ == "__main__":
    asyncio.run(main())
