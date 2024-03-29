import csv

from django.core.management.base import BaseCommand, CommandError

from foodgram.models import Ingredients

CSV_PATH = '../backend/'


class Command(BaseCommand):
    help = 'loads data from ingredients .csv file'

    def read_file(self):
        try:
            with open('ingredients.csv', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        Ingredients.objects.get_or_create(**row)
                    except Exception as e:
                        raise CommandError(
                            'Ошибка при импорте данных из ingredients.csv '
                            f'в модель Ingedients: {e}'
                        )
        except IOError:
            self.stdout.write(self.style.ERROR(
                'не может прочитать ingredients.csv'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                'ingredients.csv прочитан успешно'
            ))

    def handle(self, *args, **options):
        return self.read_file()
