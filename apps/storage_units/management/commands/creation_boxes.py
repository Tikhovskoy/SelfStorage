import random

from django.core.management.base import BaseCommand

from apps.storage_units.models import Box, Warehouse


class Command(BaseCommand):
    def handle(self, *args, **options):
        warehouses = Warehouse.objects.all()
        list_boxes = {
            "box1": [2, 1, 2.5, 2264],
            "box2": [2, 2, 2.5, 2561],
            "box3": [2, 4, 2.5, 1234],
            "box4": [5, 2, 2.1, 2345],
            "box5": [4, 4, 2.1, 3456],
            "box6": [5, 2, 2.1, 4567],
            "box7": [5, 2, 2.2, 5678],
            "box8": [5, 3, 3, 6789],
            "box9": [5, 2, 2.1, 7890],
            "box10": [5, 4, 2.2, 8901],
        }

        for warehouse in warehouses:
            for obj in range(random.randint(130, 390)):
                box = random.choice(list(list_boxes.values()))
                length, width, height, price = box

                Box.objects.create(
                    warehouse=warehouse,
                    floor=random.randint(1, 3),
                    length=length,
                    width=width,
                    height=height,
                    price=price,
                )
