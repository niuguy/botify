from django.core.management.base import BaseCommand
from bots.echo_bot import run_bot

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Telegram bot...')
        )
        run_bot()