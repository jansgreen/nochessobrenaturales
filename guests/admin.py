from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import MinistryProfile, ShowcaseCategory, ShowcaseItem


@admin.register(ShowcaseCategory)
class ShowcaseCategoryAdmin(TranslationAdmin):
    list_display = ("title", "position", "is_active", "updated_at")
    list_editable = ("position", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "headline", "description")
    ordering = ("position", "title")


@admin.register(ShowcaseItem)
class ShowcaseItemAdmin(TranslationAdmin):
    list_display = (
        "name",
        "category",
        "role",
        "position",
        "is_active",
        "updated_at",
    )
    list_editable = ("position", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "role", "description")
    ordering = ("category__position", "position", "name")


@admin.register(MinistryProfile)
class MinistryProfileAdmin(TranslationAdmin):
    list_display = (
        "name",
        "profile_type",
        "role",
        "position",
        "is_active",
        "updated_at",
    )
    list_editable = ("position", "is_active")
    list_filter = ("profile_type", "is_active")
    search_fields = ("name", "role", "introduction", "biography")
    ordering = ("position", "name")
