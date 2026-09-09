from modeltranslation.translator import TranslationOptions, register

from .models import ShowcaseCategory, ShowcaseItem


@register(ShowcaseCategory)
class ShowcaseCategoryTranslationOptions(TranslationOptions):
    fields = ("title", "headline", "accent", "description")


@register(ShowcaseItem)
class ShowcaseItemTranslationOptions(TranslationOptions):
    fields = ("role", "description", "alt_text")
