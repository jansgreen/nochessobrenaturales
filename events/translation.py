from modeltranslation.translator import TranslationOptions, register

from .models import Event


@register(Event)
class EventTranslationOptions(TranslationOptions):
    fields = ('eyebrow', 'admission_text', 'cta_text')
