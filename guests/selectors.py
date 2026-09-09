from django.db.models import Prefetch

from .models import ShowcaseCategory, ShowcaseItem


def get_active_showcase_categories():
    published_items = ShowcaseItem.objects.filter(is_active=True)
    return (
        ShowcaseCategory.objects.filter(
            is_active=True,
            items__is_active=True,
        )
        .distinct()
        .prefetch_related(
            Prefetch(
                "items",
                queryset=published_items,
                to_attr="published_items",
            )
        )
    )
