from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Banner


@admin.register(Banner)
class BannerAdmin(TranslationAdmin):
    list_display = ("title", "position", "is_active", "updated_at")
    list_editable = ("position", "is_active")
    list_filter = ("is_active", "icon")
    search_fields = ("title", "description")
    ordering = ("position", "id")
