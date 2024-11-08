from csv import DictReader

from django.core.management.base import BaseCommand

from reviews.models import Category, Genre, Title, Review, Comment, User


data_files = [
    {
        'model': Category,
        'file_path': 'static/data/category.csv',
        'fields': ('id', 'name', 'slug')
    },
    {
        'model': Genre,
        'file_path': 'static/data/genre.csv',
        'fields': ('id', 'name', 'slug')
    },
    {
        'model': Title,
        'file_path': 'static/data/titles.csv',
        'fields': ('id', 'name', 'year'),
        'foreign_keys': {'category': (Category, 'category')}
    },
    {
        'model': User,
        'file_path': 'static/data/users.csv',
        'fields': (
            'id', 'username', 'email', 'role', 'bio',
            'first_name', 'last_name'
        )
    },
    {
        'model': Review,
        'file_path': 'static/data/review.csv',
        'fields': ('id', 'text', 'score', 'pub_date'),
        'foreign_keys': {
            'title': (Title, 'title_id'),
            'author': (User, 'author')
        }
    },
    {
        'model': Comment,
        'file_path': 'static/data/comments.csv',
        'fields': ('id', 'text', 'pub_date'),
        'foreign_keys': {
            'review': (Review, 'review_id'),
            'author': (User, 'author')
        }
    },
    {
        'model': Title.genre.through,
        'file_path': 'static/data/genre_title.csv',
        'fields': ('title_id', 'genre_id'),
        'foreign_keys': {
            'title': (Title, 'title_id'),
            'genre': (Genre, 'genre_id')
        }
    },
]


class Command(BaseCommand):
    help = 'Загрузить данные из CSV-файлов в БД'

    def handle(self, *args, **kwargs):
        for data_file in data_files:
            model = data_file['model']
            print(f'Загрузка данных в таблицу {model.__name__}...')
            with open(data_file['file_path'], encoding='utf-8') as file:
                for row in DictReader(file):
                    try:
                        obj_data = {
                            field: row[field] for field in data_file['fields']
                        }
                        if 'foreign_keys' in data_file:
                            for foreign_key_field, (
                                foreign_key_model, foreign_key_value
                            ) in data_file['foreign_keys'].items():
                                obj_data[foreign_key_field] = (
                                    foreign_key_model.objects.get(
                                        id=row[foreign_key_value]
                                    )
                                )
                        model.objects.create(**obj_data)
                    except Exception as e:
                        print(
                            f'Ошибка при загрузке в таблицу {model.__name__} '
                            f'данных с id={row["id"]}: {e}'
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Данные с id={row["id"]} загружены в таблицу '
                                f'{model.__name__} успешно.'
                            )
                        )
