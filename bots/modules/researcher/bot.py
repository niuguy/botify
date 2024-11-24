from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from .handlers import start_command, help_command, message_handler, error_handler
import os
from django.core.exceptions import ImproperlyConfigured

class Bot:
    def __init__(self, token_env):
        self.token = os.getenv(token_env)
        if not self.token:
            raise ImproperlyConfigured(f"Missing {token_env} environment variable")
        self.application = None

    def setup(self):
        """Initialize the bot"""
        self.application = ApplicationBuilder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            message_handler
        ))
        self.application.add_error_handler(error_handler)

    def run(self):
        """Run the bot"""
        self.setup()
        self.application.run_polling(
            allowed_updates=["message", "callback_query"],
            close_loop=False  # Important for thread safety
        )
