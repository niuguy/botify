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


def create_app() -> Application:
    TELE_BOT_TOKEN = os.getenv("TELE_BOT_TOKEN")
    logger.info("Creating app")
    app = (
        Application.builder()
        .token(TELE_BOT_TOKEN)
        .build()
    )

    # Create a single instance of BotHandler
    bot_handler = BotHandler()

    # Register handlers using methods from the BotHandler instance
    # app.add_handler(CommandHandler("help", bot_handler.help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.echo))
    app.add_handler(CommandHandler("agents", bot_handler.agents))
    app.add_handler(
        CallbackQueryHandler(
            bot_handler.agent_selection_callback, pattern="^select_agent:"
        )
    )

    return app
