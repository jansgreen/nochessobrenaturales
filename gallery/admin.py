from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import GalleryImage


@admin.register(GalleryImage)
class GalleryImageAdmin(TranslationAdmin):
    list_display = (
        "title",
        "photographed_on",
        "position",
        "is_active",
        "updated_at",
    )
    list_editable = ("position", "is_active")
    list_filter = ("is_active", "photographed_on")
    search_fields = ("title", "description", "alt_text")
    ordering = ("position", "-photographed_on", "-created_at")
