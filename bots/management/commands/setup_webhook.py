from django.core.management.base import BaseCommand
from django.conf import settings
from bots.utils import setup_webhook, get_webhook_info

class Command(BaseCommand):
    help = 'Set up webhook for Telegram bot'

    def add_arguments(self, parser):
        parser.add_argument('domain', type=str, help='Domain URL (from ngrok)')
        parser.add_argument('--bot', type=str, help='Specific bot name to setup')

    def handle(self, *args, **options):
        domain = options['domain'].rstrip('/')
        specific_bot = options['bot']

        bots_to_setup = (
            {specific_bot: settings.TELEGRAM_BOTS[specific_bot]} 
            if specific_bot 
            else settings.TELEGRAM_BOTS
        )

        for bot_name, config in bots_to_setup.items():
            webhook_url = f"{domain}/telegram/webhook/{config['path']}/"
            result = setup_webhook(config['token'], webhook_url)
            
            if result.get('ok'):
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully set webhook for {bot_name}\n'
                        f'URL: {webhook_url}'
                    )
                )
                # Show current webhook info
                info = get_webhook_info(config['token'])
                self.stdout.write(str(info))
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to set webhook for {bot_name}: {result}'
                    )
                ) 