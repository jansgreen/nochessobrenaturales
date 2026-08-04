import gallery.models
from django.core.validators import FileExtensionValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GalleryImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=140)),
                (
                    "description",
                    models.TextField(blank=True, max_length=600),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to=gallery.models.gallery_image_upload_to,
                        validators=[
                            FileExtensionValidator(
                                allowed_extensions=(
                                    "jpg",
                                    "jpeg",
                                    "png",
                                    "webp",
                                )
                            )
                        ],
                    ),
                ),
                ("alt_text", models.CharField(max_length=180)),
                ("photographed_on", models.DateField(blank=True, null=True)),
                ("position", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "imagen de galería",
                "verbose_name_plural": "imágenes de galería",
                "ordering": (
                    "position",
                    "-photographed_on",
                    "-created_at",
                ),
            },
        ),
    ]

