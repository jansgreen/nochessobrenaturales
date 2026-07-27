import logging
import smtplib

from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from banners.models import Banner
from donations.selectors import get_donation_url
from events.selectors import (
    get_home_videos,
    get_next_event,
    get_upcoming_events,
)

from .forms import ContactForm
from .services import EmailConfigurationError, send_contact_email


logger = logging.getLogger(__name__)
CONTACT_COOLDOWN_SECONDS = 60


def _home_context(contact_form):
    events = get_upcoming_events()
    years = list(
        events.order_by()
        .values_list("starts_at__year", flat=True)
        .distinct()
    )
    if not years:
        calendar_years = "Próximamente"
    elif len(years) == 1:
        calendar_years = str(years[0])
    else:
        calendar_years = f"{min(years)}–{max(years)}"

    return {
        'banners': Banner.objects.filter(is_active=True),
        'contact_form': contact_form,
        'events': events,
        'next_event': get_next_event(),
        'calendar_years': calendar_years,
        'donation_url': get_donation_url(),
        'home_videos': get_home_videos(),
        'page_name': 'home',
    }


@require_http_methods(["GET", "POST"])
def home(request):
    contact_form = ContactForm(request.POST or None)

    if request.method == "POST":
        redirect_url = f"{reverse('home')}#contacto"

        # Honeypot: bots commonly complete every field, including this hidden one.
        if request.POST.get("website"):
            messages.success(
                request,
                "Recibimos tu mensaje. Gracias por escribirnos.",
            )
            return redirect(redirect_url)

        if contact_form.is_valid():
            now = timezone.now().timestamp()
            last_submission = request.session.get("last_contact_submission", 0)
            if now - float(last_submission) < CONTACT_COOLDOWN_SECONDS:
                messages.error(
                    request,
                    "Espera un momento antes de enviar otro mensaje.",
                )
                return redirect(redirect_url)

            contact_data = {
                key: contact_form.cleaned_data[key]
                for key in ("name", "email", "topic", "message")
            }
            try:
                send_contact_email(contact_data)
            except (
                EmailConfigurationError,
                smtplib.SMTPException,
                OSError,
                RuntimeError,
                ValueError,
            ):
                logger.exception("Could not send the website contact email.")
                messages.error(
                    request,
                    "No pudimos enviar el mensaje en este momento. "
                    "Inténtalo nuevamente más tarde.",
                )
                return render(
                    request,
                    'index.html',
                    _home_context(contact_form),
                    status=503,
                )

            request.session["last_contact_submission"] = now
            messages.success(
                request,
                "Tu mensaje fue enviado. Nuestro equipo se comunicará contigo.",
            )
            return redirect(redirect_url)

        return render(
            request,
            'index.html',
            _home_context(contact_form),
            status=400,
        )

    return render(
        request,
        'index.html',
        _home_context(contact_form),
    )
