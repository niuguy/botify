from django.core.management.base import BaseCommand
import os
import re

class Command(BaseCommand):
    help = 'Creates a new Telegram bot module'

    def add_arguments(self, parser):
        parser.add_argument('bot_name', type=str, help='Name of the bot module')
        parser.add_argument('token', type=str, help='Telegram Bot Token')

    def handle(self, *args, **options):
        bot_name = options['bot_name'].lower()
        token = options['token']
        
        # Validate bot name (convert to snake_case if needed)
        bot_name = re.sub(r'[^a-z0-9_]', '_', bot_name)
        bot_dir = f'bots/modules/{bot_name}'

        # Create directories
        os.makedirs(bot_dir, exist_ok=True)

        # Create bot files
        self._create_bot_files(bot_dir, bot_name, token)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created bot module "{bot_name}"\nYou can now start your bot using: python manage.py runbot {bot_name}')
        )

    def _create_bot_files(self, bot_dir, bot_name, token):
        # Create __init__.py
        with open(f'{bot_dir}/__init__.py', 'w') as f:
            f.write('')

        # Create handlers.py
        with open(f'{bot_dir}/handlers.py', 'w') as f:
            f.write('''from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Bot is running.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Help message here.')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Error occurred: {context.error}')
''')

        # Create bot.py
        with open(f'{bot_dir}/bot.py', 'w') as f:
            f.write('''from telegram.ext import ApplicationBuilder, CommandHandler
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
        self.application.run_polling(
            allowed_updates=["message", "callback_query"],
            close_loop=False  # Important for thread safety
        )
''')

        # Create config.py
        with open(f'{bot_dir}/config.py', 'w') as f:
            f.write(f'''# Bot configuration settings
CONFIG = {{
    "enabled": True,
    "token": "{token}",
    "settings": {{
        # Add your bot specific settings here
    }}
}}
''')
