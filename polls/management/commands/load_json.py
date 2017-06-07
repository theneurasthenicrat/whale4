from django.core.management.base import BaseCommand, CommandError
import argparse, json
from polls.models import VotingPoll, Candidate, VotingScore
from accounts.models import WhaleUser, User
from datetime import date

class Command(BaseCommand):
    """Loads a JSON file"""
    help = 'Loads a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'))
        parser.add_argument('title')
        parser.add_argument('description')

    def handle(self, *args, **options):
        poll_object = json.load(options['file'])

        poll = VotingPoll(
            title=options['title'],
            description=options['description'],
            admin=WhaleUser.objects.get(id='b6bc6c9f-e2f5-4a7c-92a8-95ad819c4064'),
            preference_model=poll_object['preferenceModel']['id'],
            closing_date = date.today()
        )
        poll.save()

        self.stdout.write(self.style.SUCCESS('Successfully created poll "%s"' % poll.id))
        
        candidates = []
        for c in poll_object['candidates']:
            candidates.append(Candidate(
                poll=poll,
                candidate=c))
            candidates[-1].save()

        self.stdout.write(self.style.SUCCESS('Successfully added %d candidates' % len(candidates)))

        for v in poll_object['votes']:
            voter = User(nickname=v['name'])
            voter.save()
            for i, sc in enumerate(v['values']):
                VotingScore(
                    candidate=candidates[i],
                    voter=voter,
                    value=sc).save()

        self.stdout.write(self.style.SUCCESS('Successfully added %d votes' % len(poll_object['votes'])))

