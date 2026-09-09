from modeltranslation.translator import TranslationOptions, register

from .models import MinistryProfile, ShowcaseCategory, ShowcaseItem


@register(ShowcaseCategory)
class ShowcaseCategoryTranslationOptions(TranslationOptions):
    fields = ("title", "headline", "accent", "description")


@register(ShowcaseItem)
class ShowcaseItemTranslationOptions(TranslationOptions):
    fields = ("role", "description", "alt_text")


@register(MinistryProfile)
class MinistryProfileTranslationOptions(TranslationOptions):
    fields = ("role", "introduction", "biography", "alt_text")
