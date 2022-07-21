import csv
import os
from typing import Dict

from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Comment, Genre, Review, Title, User

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)

CSV_DIR = os.path.join(BASE_DIR, "static/data")
CSV_FILES = (
    "users",
    "category",
    "genre",
    "titles",
    "genre_title",
    "review",
    "comments",
)


class Command(BaseCommand):
    help = "Import static csv data to DB"

    @staticmethod
    def clear_tables():
        User.objects.all().delete()
        Category.objects.all().delete()
        Genre.objects.all().delete()
        Title.objects.all().delete()
        Review.objects.all().delete()
        Comment.objects.all().delete()

    @staticmethod
    def create_row(data: Dict, name: str):
        if name == "users":
            User.objects.create(**data)

        elif name == "category":
            Category.objects.create(**data)

        elif name == "genre":
            Genre.objects.create(**data)

        elif name == "titles":
            data["category_id"] = data["category"]
            del data["category"]

            Title.objects.create(**data)

        elif name == "genre_title":
            title = Title.objects.get(id=data["title_id"])
            genre = Genre.objects.get(id=data["genre_id"])

            title.genre.add(genre)
            title.save()

        elif name == "review":
            data["author_id"] = data["author"]
            del data["author"]

            Review.objects.create(**data)

        elif name == "comments":
            data["author_id"] = data["author"]
            del data["author"]

            Comment.objects.create(**data)

    def handle(self, *args, **options):
        self.clear_tables()

        for csv_filename in CSV_FILES:
            path_to_csv_file = f"{CSV_DIR}/{csv_filename}.csv"

            try:
                csv_file = open(path_to_csv_file, newline="")
            except OSError:
                raise CommandError('Failed to open "%s"' % path_to_csv_file)

            rows = csv.DictReader(csv_file)

            try:
                for row in list(rows):
                    self.create_row(row, csv_filename)
            except csv.Error as e:
                raise CommandError(
                    "file {}, line {}: {}".format(
                        path_to_csv_file, rows.line_num, e
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully imported "%s"' % csv_file.name
                )
            )
