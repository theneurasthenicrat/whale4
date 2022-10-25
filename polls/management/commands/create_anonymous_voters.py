"""Creates a set of anonymous voters from a list of email addresses and logins"""

from django.core.management.base import BaseCommand
from accounts.models import WhaleUserAnonymous
from polls.models import VotingPoll, VotingScore


class Command(BaseCommand):
    """Creates a set of anonymous voters from a list of email addresses and logins"""
    help = "Creates a set of anonymous voters from a list of email addresses and logins"

    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs=1, type=str,
                            help="should correspond to a valid anonymous voting poll")
        parser.add_argument('input_csv_file', nargs=1, type=str,
                            help="the input csv file should be a ';' separated two-columns csv file"
                            + " formatted as 'login;email'")
        parser.add_argument('output_csv_file', nargs=1, type=str,
                            help="the command outputs a CSV file formatted as 'login;certificate'")

    def handle(self, *args, **options):
        poll = VotingPoll.objects.get(id=options['poll_id'][0])

        VotingScore.objects.filter(candidate__poll__id=poll.id).delete()
        WhaleUserAnonymous.objects.filter(poll__id=poll.id).delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared the poll'))

        csv_filename = options['input_csv_file'][0]

        voters = {}
        with open(csv_filename, 'r') as csv_file:
            for row in csv_file:
                login, email = row.strip().split(';')
                voters[login] = email
        certificates = {}

        for login, email in voters.items():
            certi = WhaleUserAnonymous.id_generator()
            WhaleUserAnonymous.objects.create(
                nickname=WhaleUserAnonymous.nickname_generator(poll.id),
                email=email,
                certificate=WhaleUserAnonymous.encodeAES(certi),
                poll=poll
            )
            certificates[login] = certi

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(certificates)} voters'))

        csv_filename = options['output_csv_file'][0]

        with open(csv_filename, 'w') as csv_file:
            for login, certi in certificates.items():
                csv_file.write(f'{login};{certi}\n')

        self.stdout.write(self.style.SUCCESS('Successfully wrote output CSV file'))
        self.stdout.write(self.style.SUCCESS(f'Election number: {poll.id}'))
