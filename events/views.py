from django.core.paginator import Paginator
from django.shortcuts import render

from donations.selectors import get_donation_url

from .selectors import get_active_videos


def video_gallery(request):
    paginator = Paginator(get_active_videos(), 9)
    page_obj = paginator.get_page(request.GET.get("pagina"))
    return render(
        request,
        "events/gallery.html",
        {
            "page_obj": page_obj,
            "video_count": paginator.count,
            "donation_url": get_donation_url(),
            "page_name": "events",
        },
    )

