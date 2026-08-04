from modeltranslation.translator import TranslationOptions, register

from .models import GalleryImage


@register(GalleryImage)
class GalleryImageTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'alt_text')
