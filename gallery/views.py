from django.core.paginator import Paginator
from django.shortcuts import render

from donations.selectors import get_donation_url

from .selectors import get_active_gallery_images


def image_gallery(request):
    paginator = Paginator(get_active_gallery_images(), 12)
    page_obj = paginator.get_page(request.GET.get("pagina"))
    page_range = paginator.get_elided_page_range(
        page_obj.number,
        on_each_side=1,
        on_ends=1,
    )
    return render(
        request,
        "gallery/gallery.html",
        {
            "page_obj": page_obj,
            "page_range": page_range,
            "pagination_ellipsis": Paginator.ELLIPSIS,
            "image_count": paginator.count,
            "donation_url": get_donation_url(),
            "page_name": "gallery",
        },
    )

