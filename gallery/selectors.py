from .models import GalleryImage


def get_active_gallery_images():
    return GalleryImage.objects.filter(is_active=True)

