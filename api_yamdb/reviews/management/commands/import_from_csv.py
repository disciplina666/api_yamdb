from csv import DictReader
from django.conf import settings
from django.core.management import BaseCommand
from pathlib import Path

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title

from .models import CustomUser

DATA_DB = {
    CustomUser: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
    GenreTitle: 'genre_title.csv'
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        data_dir = Path(settings.BASE_DIR) / 'static' / 'data'
        for model, filename in DATA_DB.items():
            file_path = data_dir / filename
            try:
                with file_path.open('r', encoding='utf-8') as csv_file:
                    reader = DictReader(csv_file)
                    objects_to_create = []
                    for row in reader:
                        data = {}
                        for field in row:
                            value = row[field]
                            data[field] = value.strip()
                        obj = model(**data)
                        objects_to_create.append(obj)
                    model.objects.bulk_create(objects_to_create)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Данные для {model.__name__} успешно загружены.'
                    )
                )
            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(f'Файл {filename} не найден!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при импорте {filename}: {e}')
                )
