from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Create default tags'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#49B64E', 'slug': 'dinner'},
            {'name': 'Ужин', 'color': '#8775D2', 'slug': 'supper'},
            {'name': 'Сладенькое', 'color': '#c9a2bf', 'slug': 'sweet'},
            {'name': 'Острое', 'color': '#cc0000', 'slug': 'sharp'},
        ]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)

        self.stdout.write(self.style.SUCCESS(
            '==>> Стандартные теги успешно загружены в БД <<=='
        ))
