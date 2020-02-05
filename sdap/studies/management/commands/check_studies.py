from django.core.management.base import BaseCommand, CommandError
from sdap.studies.models import ExpressionStudy, ExpressionData
from django.utils.timezone import now
from datetime import timedelta
import sys

class Command(BaseCommand):
    help = 'Was a signature modified in the last x days?'

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            default=7,
            type=int,
            help="Number of days elapsed : default 7"
        )

    def handle(self, *args, **options):
        if not ExpressionStudy.objects.filter(updated_at__gte = now()-timedelta(days=options['days'])).exists() or ExpressionStudy.objects.filter(created_at__gte = now()-timedelta(days=options['days'])):
            print('False')
            sys.exit(1)
        print('True')
