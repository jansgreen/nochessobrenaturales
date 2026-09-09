from django.db import migrations


def create_locations_category(apps, schema_editor):
    ShowcaseCategory = apps.get_model("guests", "ShowcaseCategory")
    ShowcaseCategory.objects.get_or_create(
        title_es="Locaciones",
        defaults={
            "title": "Locaciones",
            "title_en": "Locations",
            "title_pt": "Localizações",
            "headline": "Encuentra tu próxima locación.",
            "headline_es": "Encuentra tu próxima locación.",
            "headline_en": "Find your nearest location.",
            "headline_pt": "Encontre o local mais próximo.",
            "accent": "Un lugar para ti.",
            "accent_es": "Un lugar para ti.",
            "accent_en": "A place for you.",
            "accent_pt": "Um lugar para si.",
            "description": (
                "Conoce nuestras locaciones y encuentra el lugar donde podrás "
                "acompañarnos en comunidad."
            ),
            "description_es": (
                "Conoce nuestras locaciones y encuentra el lugar donde podrás "
                "acompañarnos en comunidad."
            ),
            "description_en": (
                "Explore our locations and find the place where you can join "
                "us in community."
            ),
            "description_pt": (
                "Conheça os nossos locais e encontre o lugar onde poderá "
                "juntar-se a nós em comunidade."
            ),
            "position": 10,
            "is_active": True,
        },
    )


def remove_empty_locations_category(apps, schema_editor):
    ShowcaseCategory = apps.get_model("guests", "ShowcaseCategory")
    ShowcaseCategory.objects.filter(
        title_es="Locaciones",
        items__isnull=True,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("guests", "0002_showcase_categories"),
    ]

    operations = [
        migrations.RunPython(
            create_locations_category,
            remove_empty_locations_category,
        ),
    ]
