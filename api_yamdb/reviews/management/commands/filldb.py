from django.core.management.base import BaseCommand
import csv
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('static/data/users.csv') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                User.objects.get_or_create(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=row[3],
                    bio=row[4],
                    first_name=row[5],
                    last_name=row[6],
                )
