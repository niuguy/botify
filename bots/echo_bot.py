from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os
from dotenv import load_dotenv

load_dotenv()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    await update.message.reply_text(
        "👋 Hello! I'm an echo bot. Send me any message and I'll repeat it back to you!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help command"""
    await update.message.reply_text(
        "Send me any message and I'll echo it back to you!\n"
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message"""
    await update.message.reply_text(update.message.text)

def run_bot():
    """Initialize and run the bot"""
    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("No token provided!")

    # Create application
    application = ApplicationBuilder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the bot
    application.run_polling()