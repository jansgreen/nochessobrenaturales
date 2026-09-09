from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import MinistryProfile, ShowcaseItem


@receiver(pre_save, sender=ShowcaseItem)
def remember_replaced_photo(sender, instance, **kwargs):
    instance._replaced_photo_name = ""
    if not instance.pk:
        return

    previous = sender.objects.filter(pk=instance.pk).only("photo").first()
    if previous and previous.photo.name != instance.photo.name:
        instance._replaced_photo_name = previous.photo.name


@receiver(post_save, sender=ShowcaseItem)
def delete_replaced_photo(sender, instance, **kwargs):
    previous_name = getattr(instance, "_replaced_photo_name", "")
    if previous_name:
        instance.photo.storage.delete(previous_name)


@receiver(post_delete, sender=ShowcaseItem)
def delete_removed_photo(sender, instance, **kwargs):
    if instance.photo and instance.photo.name:
        instance.photo.storage.delete(instance.photo.name)


@receiver(pre_save, sender=MinistryProfile)
def remember_replaced_ministry_photo(sender, instance, **kwargs):
    instance._replaced_photo_name = ""
    if not instance.pk:
        return

    previous = sender.objects.filter(pk=instance.pk).only("photo").first()
    if previous and previous.photo.name != instance.photo.name:
        instance._replaced_photo_name = previous.photo.name


@receiver(post_save, sender=MinistryProfile)
def delete_replaced_ministry_photo(sender, instance, **kwargs):
    previous_name = getattr(instance, "_replaced_photo_name", "")
    if previous_name:
        instance.photo.storage.delete(previous_name)


@receiver(post_delete, sender=MinistryProfile)
def delete_removed_ministry_photo(sender, instance, **kwargs):
    if instance.photo and instance.photo.name:
        instance.photo.storage.delete(instance.photo.name)
