from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import GalleryImage


@receiver(pre_save, sender=GalleryImage)
def remember_replaced_image(sender, instance, **kwargs):
    instance._replaced_image_name = ""
    if not instance.pk:
        return

    previous = sender.objects.filter(pk=instance.pk).only("image").first()
    if previous and previous.image.name != instance.image.name:
        instance._replaced_image_name = previous.image.name


@receiver(post_save, sender=GalleryImage)
def delete_replaced_image(sender, instance, **kwargs):
    previous_name = getattr(instance, "_replaced_image_name", "")
    if previous_name:
        instance.image.storage.delete(previous_name)


@receiver(post_delete, sender=GalleryImage)
def delete_removed_image(sender, instance, **kwargs):
    if instance.image and instance.image.name:
        instance.image.storage.delete(instance.image.name)

