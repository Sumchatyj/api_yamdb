import csv

from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User


def fill_user_data(path):
    try:
        with open(path, encoding="utf8") as f:
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
    except IOError:
        print('no users data')


def fill_category_data(path):
    try:
        with open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                Category.objects.get_or_create(
                    id=row[0],
                    name=row[1],
                    slug=row[2],
                )
    except IOError:
        print('no category data')


def fill_title_data(path):
    try:
        with open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                Title.objects.get_or_create(
                    id=row[0],
                    name=row[1],
                    year=row[2],
                    category=Category.objects.get(pk=row[3]),
                )
    except IOError:
        print('no title data')


def fill_review_data(path):
    try:
        with open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                Review.objects.get_or_create(
                    id=row[0],
                    title=Title.objects.get(pk=row[1]),
                    text=row[2],
                    author=User.objects.get(pk=row[3]),
                    score=row[4],
                    pub_date=row[5],
                )
    except IOError:
        print('no review data')


def fill_comments_data(path):
    try:
        with open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                Comment.objects.get_or_create(
                    id=row[0],
                    review=Review.objects.get(pk=row[1]),
                    text=row[2],
                    author=User.objects.get(pk=row[3]),
                    pub_date=row[4],
                )
    except IOError:
        print('no comments data')


def fill_genre_data(path):
    try:
        with open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row[0],
                    name=row[1],
                    slug=row[2],
                )
    except IOError:
        print('no genre data')


def fill_genre_title_data(path):
    try:
        with open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                GenreTitle.objects.get_or_create(
                    id=row[0],
                    title=Title.objects.get(pk=row[1]),
                    genre=Genre.objects.get(pk=row[2])
                )
    except IOError:
        print('no genre_title data')


class Command(BaseCommand):
    def handle(self, *args, **options):
        fill_user_data('static/data/users.csv')
        fill_category_data('static/data/category.csv')
        fill_title_data('static/data/titles.csv')
        fill_review_data('static/data/review.csv')
        fill_comments_data('static/data/comments.csv')
        fill_genre_data('static/data/genre.csv')
        fill_genre_title_data('static/data/genre_title.csv')
        print('fixtures added to DB')
