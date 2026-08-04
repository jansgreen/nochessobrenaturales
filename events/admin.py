from django.contrib import admin
from django.db import transaction
from modeltranslation.admin import TranslationAdmin

from .models import Event, YouTubeVideo


@admin.register(Event)
class EventAdmin(TranslationAdmin):
    list_display = (
        "starts_at",
        "eyebrow",
        "admission_text",
        "is_featured",
        "is_published",
    )
    list_filter = ("is_featured", "is_published", "starts_at")
    search_fields = ("eyebrow", "admission_text")
    ordering = ("starts_at",)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if obj.is_featured:
            Event.objects.exclude(pk=obj.pk).update(is_featured=False)
        super().save_model(request, obj, form, change)


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = (
        "display_title",
        "channel_title",
        "position",
        "show_on_home",
        "is_active",
        "api_synced_at",
    )
    list_editable = ("position", "show_on_home", "is_active")
    list_filter = ("show_on_home", "is_active")
    search_fields = ("title", "channel_title", "youtube_id")
    readonly_fields = (
        "youtube_id",
        "title",
        "channel_title",
        "thumbnail_url",
        "published_at",
        "api_synced_at",
    )
