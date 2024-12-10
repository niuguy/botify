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

from botify.handlers.base import (
    help_command,
    echo,
    agents,
    agent_selection_callback,
)
from botify.logging.logger import logger


def create_app() -> Application:
    logger.info("Creating app")
    app = (
        Application.builder()
        .token("7545484988:AAHgIZFvd1Fi52MI9v3HROZgO9MhYFNBGak")
        .build()
    )
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(CommandHandler("agents", agents))
    app.add_handler(
        CallbackQueryHandler(agent_selection_callback, pattern="^select_agent:")
    )
    return app
