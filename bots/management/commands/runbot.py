from django.core.management.base import BaseCommand
import importlib
import signal
import sys

class Command(BaseCommand):
    help = 'Runs a specific Telegram bot'

    def add_arguments(self, parser):
        parser.add_argument('bot_name', type=str, help='Name of the bot to run')

    def handle(self, *args, **options):
        bot_name = options['bot_name']
        
        try:
            # Import bot modules
            config_module = importlib.import_module(f'bots.modules.{bot_name}.config')
            bot_module = importlib.import_module(f'bots.modules.{bot_name}.bot')

            if not config_module.CONFIG['enabled']:
                self.stdout.write(self.style.ERROR(f'Bot "{bot_name}" is disabled in config'))
                return

            # Create bot instance
            bot = bot_module.Bot(config_module.CONFIG['token'])
            self.stdout.write(self.style.SUCCESS(f'Starting bot "{bot_name}"...'))

            # Setup signal handler for graceful shutdown
            def signal_handler(signum, frame):
                self.stdout.write(self.style.SUCCESS('\nStopping bot...'))
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Run the bot
            bot.run()

        except ImportError:
            self.stdout.write(self.style.ERROR(f'Bot module "{bot_name}" not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running bot: {str(e)}'))