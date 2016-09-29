from django.core.management.base import BaseCommand, CommandError
from polls.utils import dump_polls_as_json

class Command(BaseCommand):
    """Dumps all the polls of the database"""
    help = 'Dumps all the polls of the database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        dump_polls_as_json()
        self.stdout.write(self.style.SUCCESS('Successfully dumped all the polls'))
