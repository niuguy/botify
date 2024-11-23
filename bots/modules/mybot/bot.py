from telegram.ext import ApplicationBuilder, CommandHandler
from .handlers import start_command, help_command, error_handler

class Bot:
    def __init__(self, token):
        self.token = token
        self.application = None

    def setup(self):
        """Initialize the bot"""
        self.application = ApplicationBuilder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler('start', start_command))
        self.application.add_handler(CommandHandler('help', help_command))
        self.application.add_error_handler(error_handler)

    def run(self):
        """Run the bot"""
        self.setup()
        self.application.run_polling(allowed_updates=["message", "callback_query"])
