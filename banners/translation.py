from modeltranslation.translator import TranslationOptions, register

from .models import Banner


@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'button_text')
