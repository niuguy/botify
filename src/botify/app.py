#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from botify.handlers.bot_handler import BotHandler
from botify.logging.logger import logger
import os
import asyncio

def create_app() -> Application:
    TELE_BOT_TOKEN = os.getenv("TELE_BOT_TOKEN")
    logger.info("Creating app")
    bot_handler = BotHandler()
    app = (
        Application.builder()
        .token(TELE_BOT_TOKEN).post_init(bot_handler.post_init)
        .build()
    )

    # Register handlers using methods from the BotHandler instance
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.echo))
    app.add_handler(CommandHandler("agents", bot_handler.agents))
    app.add_handler(
        CallbackQueryHandler(
            bot_handler.agent_selection_callback, pattern="^select_agent:"
        )
    )

    return app

def run_bot():
    app = create_app()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        logger.info("Running bot")
        loop.run_until_complete(app.initialize())
        loop.run_until_complete(app.start())
        loop.run_until_complete(app.updater.start_polling())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Stopping bot")
    finally:
        loop.run_until_complete(app.updater.stop())
        loop.run_until_complete(app.stop())
        loop.run_until_complete(app.shutdown())
        loop.close()

def run():
    logger.info("Starting bot process")
    run_bot()
