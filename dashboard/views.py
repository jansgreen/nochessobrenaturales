from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from banners.forms import BannerForm
from banners.models import Banner
from donations.forms import DonationSettingsForm
from donations.models import DonationSettings
from donations.selectors import get_donation_url
from events.forms import EventForm, YouTubeVideoForm
from events.models import Event, YouTubeVideo
from events.selectors import (
    get_active_videos,
    get_next_event,
    get_upcoming_events,
)
from events.youtube_api import (
    YouTubeAPIConfigurationError,
    YouTubeAPIError,
    YouTubeVideoUnavailable,
    fetch_youtube_metadata,
)
from gallery.forms import GalleryImageForm
from gallery.models import GalleryImage
from guests.forms import ShowcaseCategoryForm, ShowcaseItemForm
from guests.models import ShowcaseCategory, ShowcaseItem

from .decorators import staff_required


@login_required
def dashboard_home(request):
    context = {
        "next_event": get_next_event(),
        "donation_url": get_donation_url(),
    }
    if request.user.is_staff:
        context["banner_count"] = Banner.objects.count()
        context["active_banner_count"] = Banner.objects.filter(is_active=True).count()
        context["event_count"] = Event.objects.count()
        context["upcoming_event_count"] = get_upcoming_events().count()
        context["video_count"] = YouTubeVideo.objects.count()
        context["active_video_count"] = get_active_videos().count()
        context["gallery_image_count"] = GalleryImage.objects.count()
        context["active_gallery_image_count"] = GalleryImage.objects.filter(
            is_active=True
        ).count()
        context["showcase_category_count"] = ShowcaseCategory.objects.count()
        context["active_showcase_category_count"] = ShowcaseCategory.objects.filter(
            is_active=True
        ).count()
        context["showcase_item_count"] = ShowcaseItem.objects.count()
        context["active_showcase_item_count"] = ShowcaseItem.objects.filter(
            is_active=True,
            category__is_active=True,
        ).count()
    return render(request, 'dash.html', context)


@staff_required
@require_http_methods(["GET", "POST"])
def donation_settings(request):
    instance = (
        DonationSettings.objects.filter(pk=1).first()
        or DonationSettings(pk=1)
    )
    form = DonationSettingsForm(request.POST or None, instance=instance)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "La configuración de donaciones fue actualizada.",
        )
        return redirect("dashboard:donation_settings")

    return render(
        request,
        "backend/donations/settings.html",
        {
            "form": form,
            "donation_url": instance.paypal_url,
        },
    )


def _save_youtube_video(request, form):
    video = form.save(commit=False)
    should_sync = (
        "youtube_url" in form.changed_data
        or not video.api_synced_at
    )

    if should_sync:
        try:
            metadata = fetch_youtube_metadata(video.youtube_id)
        except YouTubeVideoUnavailable as error:
            form.add_error("youtube_url", str(error))
            return None
        except YouTubeAPIConfigurationError:
            messages.warning(
                request,
                "El video fue guardado. Configura YOUTUBE_API_KEY para "
                "obtener automáticamente su título y canal.",
            )
        except YouTubeAPIError:
            messages.warning(
                request,
                "El video fue guardado, pero YouTube no respondió. "
                "Puedes sincronizarlo después.",
            )
        else:
            video.apply_api_metadata(metadata)

    video.save()
    return video


@staff_required
def youtube_video_list(request):
    return render(
        request,
        "backend/youtube/video_list.html",
        {
            "videos": YouTubeVideo.objects.all(),
            "youtube_api_configured": bool(settings.YOUTUBE_API_KEY),
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def youtube_video_create(request):
    form = YouTubeVideoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        video = _save_youtube_video(request, form)
        if video:
            messages.success(request, "El video fue agregado a la galería.")
            return redirect("dashboard:youtube_video_list")

    return render(
        request,
        "backend/youtube/video_form.html",
        {
            "form": form,
            "page_title": "Agregar video",
            "submit_label": "Agregar video",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def youtube_video_update(request, pk):
    video = get_object_or_404(YouTubeVideo, pk=pk)
    form = YouTubeVideoForm(
        request.POST or None,
        instance=video,
    )
    if request.method == "POST" and form.is_valid():
        saved_video = _save_youtube_video(request, form)
        if saved_video:
            messages.success(
                request,
                "La configuración del video fue actualizada.",
            )
            return redirect("dashboard:youtube_video_list")

    return render(
        request,
        "backend/youtube/video_form.html",
        {
            "form": form,
            "video": video,
            "page_title": "Editar video",
            "submit_label": "Guardar cambios",
        },
    )


@staff_required
@require_http_methods(["POST"])
def youtube_video_sync(request, pk):
    video = get_object_or_404(YouTubeVideo, pk=pk)
    try:
        metadata = fetch_youtube_metadata(video.youtube_id)
    except YouTubeAPIConfigurationError as error:
        messages.warning(request, str(error))
    except (YouTubeVideoUnavailable, YouTubeAPIError) as error:
        messages.error(request, str(error))
    else:
        video.apply_api_metadata(metadata)
        video.save()
        messages.success(
            request,
            f'Los datos de “{video.display_title}” fueron sincronizados.',
        )
    return redirect("dashboard:youtube_video_list")


@staff_required
@require_http_methods(["GET", "POST"])
def youtube_video_delete(request, pk):
    video = get_object_or_404(YouTubeVideo, pk=pk)
    if request.method == "POST":
        title = video.display_title
        video.delete()
        messages.success(request, f'El video “{title}” fue eliminado.')
        return redirect("dashboard:youtube_video_list")

    return render(
        request,
        "backend/youtube/video_confirm_delete.html",
        {"video": video},
    )


@staff_required
def banner_list(request):
    banners = Banner.objects.all()
    return render(
        request,
        "backend/banners/banner_list.html",
        {"banners": banners},
    )


@staff_required
@require_http_methods(["GET", "POST"])
def banner_create(request):
    form = BannerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        banner = form.save()
        messages.success(request, f'El banner “{banner.title}” fue creado.')
        return redirect("dashboard:banner_list")

    return render(
        request,
        "backend/banners/banner_form.html",
        {
            "form": form,
            "page_title": "Crear banner",
            "submit_label": "Crear banner",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def banner_update(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    form = BannerForm(request.POST or None, instance=banner)
    if request.method == "POST" and form.is_valid():
        banner = form.save()
        messages.success(request, f'El banner “{banner.title}” fue actualizado.')
        return redirect("dashboard:banner_list")

    return render(
        request,
        "backend/banners/banner_form.html",
        {
            "form": form,
            "banner": banner,
            "page_title": "Editar banner",
            "submit_label": "Guardar cambios",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == "POST":
        title = banner.title
        banner.delete()
        messages.success(request, f'El banner “{title}” fue eliminado.')
        return redirect("dashboard:banner_list")

    return render(
        request,
        "backend/banners/banner_confirm_delete.html",
        {"banner": banner},
    )


@staff_required
def event_list(request):
    events = Event.objects.all()
    return render(
        request,
        "backend/events/event_list.html",
        {
            "events": events,
            "next_event": get_next_event(),
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def event_create(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save()
        messages.success(request, f'El evento “{event.full_date_label}” fue creado.')
        return redirect("dashboard:event_list")

    return render(
        request,
        "backend/events/event_form.html",
        {
            "form": form,
            "page_title": "Crear evento",
            "submit_label": "Crear evento",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        event = form.save()
        messages.success(
            request,
            f'El evento “{event.full_date_label}” fue actualizado.',
        )
        return redirect("dashboard:event_list")

    return render(
        request,
        "backend/events/event_form.html",
        {
            "form": form,
            "event": event,
            "page_title": "Editar evento",
            "submit_label": "Guardar cambios",
        },
    )


@staff_required
@require_http_methods(["POST"])
def event_feature(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.is_published = True
    event.is_featured = True
    event.save(update_fields=("is_published", "is_featured", "updated_at"))
    messages.success(
        request,
        f'“{event.full_date_label}” ahora es el próximo encuentro.',
    )
    return redirect("dashboard:event_list")


@staff_required
@require_http_methods(["GET", "POST"])
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        label = event.full_date_label
        event.delete()
        messages.success(request, f'El evento “{label}” fue eliminado.')
        return redirect("dashboard:event_list")

    return render(
        request,
        "backend/events/event_confirm_delete.html",
        {"event": event},
    )


@staff_required
def gallery_image_list(request):
    paginator = Paginator(GalleryImage.objects.all(), 10)
    page_obj = paginator.get_page(request.GET.get("pagina"))
    return render(
        request,
        "backend/gallery/image_list.html",
        {"page_obj": page_obj},
    )


@staff_required
@require_http_methods(["GET", "POST"])
def gallery_image_create(request):
    form = GalleryImageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        image = form.save()
        messages.success(
            request,
            f'La imagen “{image.title}” fue agregada a la galería.',
        )
        return redirect("dashboard:gallery_image_list")

    return render(
        request,
        "backend/gallery/image_form.html",
        {
            "form": form,
            "page_title": "Agregar imagen",
            "submit_label": "Agregar imagen",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def gallery_image_update(request, pk):
    gallery_image = get_object_or_404(GalleryImage, pk=pk)
    form = GalleryImageForm(
        request.POST or None,
        request.FILES or None,
        instance=gallery_image,
    )
    if request.method == "POST" and form.is_valid():
        gallery_image = form.save()
        messages.success(
            request,
            f'La imagen “{gallery_image.title}” fue actualizada.',
        )
        return redirect("dashboard:gallery_image_list")

    return render(
        request,
        "backend/gallery/image_form.html",
        {
            "form": form,
            "gallery_image": gallery_image,
            "page_title": "Editar imagen",
            "submit_label": "Guardar cambios",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def gallery_image_delete(request, pk):
    gallery_image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == "POST":
        title = gallery_image.title
        gallery_image.delete()
        messages.success(request, f'La imagen “{title}” fue eliminada.')
        return redirect("dashboard:gallery_image_list")

    return render(
        request,
        "backend/gallery/image_confirm_delete.html",
        {"gallery_image": gallery_image},
    )


@staff_required
def showcase_list(request):
    return render(
        request,
        "backend/showcase/showcase_list.html",
        {"showcase_categories": ShowcaseCategory.objects.prefetch_related("items")},
    )


@staff_required
@require_http_methods(["GET", "POST"])
def showcase_category_create(request):
    form = ShowcaseCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(
            request,
            f'La categoría “{category.title}” fue creada.',
        )
        return redirect("dashboard:showcase_list")

    return render(
        request,
        "backend/showcase/category_form.html",
        {
            "form": form,
            "page_title": "Crear categoría",
            "submit_label": "Crear categoría",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def showcase_category_update(request, pk):
    showcase_category = get_object_or_404(ShowcaseCategory, pk=pk)
    form = ShowcaseCategoryForm(
        request.POST or None,
        instance=showcase_category,
    )
    if request.method == "POST" and form.is_valid():
        showcase_category = form.save()
        messages.success(
            request,
            f'La categoría “{showcase_category.title}” fue actualizada.',
        )
        return redirect("dashboard:showcase_list")

    return render(
        request,
        "backend/showcase/category_form.html",
        {
            "form": form,
            "showcase_category": showcase_category,
            "page_title": "Editar categoría",
            "submit_label": "Guardar cambios",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def showcase_category_delete(request, pk):
    showcase_category = get_object_or_404(ShowcaseCategory, pk=pk)
    if request.method == "POST":
        title = showcase_category.title
        showcase_category.delete()
        messages.success(request, f'La categoría “{title}” fue eliminada.')
        return redirect("dashboard:showcase_list")

    return render(
        request,
        "backend/showcase/category_confirm_delete.html",
        {"showcase_category": showcase_category},
    )


@staff_required
@require_http_methods(["GET", "POST"])
def showcase_item_create(request):
    initial = {}
    if category_id := request.GET.get("categoria"):
        initial["category"] = category_id
    form = ShowcaseItemForm(
        request.POST or None,
        request.FILES or None,
        initial=initial,
    )
    if request.method == "POST" and form.is_valid():
        item = form.save()
        messages.success(request, f'La tarjeta “{item.name}” fue agregada.')
        return redirect("dashboard:showcase_list")

    return render(
        request,
        "backend/showcase/item_form.html",
        {
            "form": form,
            "page_title": "Agregar tarjeta",
            "submit_label": "Agregar tarjeta",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def showcase_item_update(request, pk):
    showcase_item = get_object_or_404(ShowcaseItem, pk=pk)
    form = ShowcaseItemForm(
        request.POST or None,
        request.FILES or None,
        instance=showcase_item,
    )
    if request.method == "POST" and form.is_valid():
        showcase_item = form.save()
        messages.success(
            request,
            f'La tarjeta “{showcase_item.name}” fue actualizada.',
        )
        return redirect("dashboard:showcase_list")

    return render(
        request,
        "backend/showcase/item_form.html",
        {
            "form": form,
            "showcase_item": showcase_item,
            "page_title": "Editar tarjeta",
            "submit_label": "Guardar cambios",
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def showcase_item_delete(request, pk):
    showcase_item = get_object_or_404(ShowcaseItem, pk=pk)
    if request.method == "POST":
        name = showcase_item.name
        showcase_item.delete()
        messages.success(request, f'La tarjeta “{name}” fue eliminada.')
        return redirect("dashboard:showcase_list")

    return render(
        request,
        "backend/showcase/item_confirm_delete.html",
        {"showcase_item": showcase_item},
    )
