from django.core.management.base import BaseCommand
import signal
import sys

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        from bot.telegram.bot import Bot
        
        def signal_handler(sig, frame):
            print('Stopping bot...')
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        bot = Bot(token_env='TELEGRAM_BOT_TOKEN')
        bot.run()
    