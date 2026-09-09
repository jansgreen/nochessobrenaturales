from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


ERROR_PAGES = {
    400: {
        "eyebrow": _("Solicitud no válida"),
        "title": _("No pudimos procesar esta solicitud."),
        "message": _("Revisa la información e inténtalo nuevamente."),
    },
    403: {
        "eyebrow": _("Acceso restringido"),
        "title": _("No tienes permiso para entrar aquí."),
        "message": _(
            "Si crees que deberías tener acceso, inicia sesión con una "
            "cuenta autorizada."
        ),
        "secondary_label": _("Iniciar sesión"),
        "secondary_url_name": "accounts:login",
    },
    404: {
        "eyebrow": _("Página no encontrada"),
        "title": _("Este camino no lleva a ninguna página."),
        "message": _(
            "Es posible que el enlace haya cambiado o que la dirección "
            "no sea correcta."
        ),
        "secondary_label": _("Ver próximos eventos"),
        "secondary_url_name": "events:gallery",
    },
    500: {
        "eyebrow": _("Algo salió mal"),
        "title": _("El sitio necesita un momento."),
        "message": _(
            "No pudimos completar la operación. Inténtalo nuevamente "
            "dentro de unos minutos."
        ),
    },
}


def _render_error(request, status_code):
    context = {
        "status_code": status_code,
        **ERROR_PAGES[status_code],
        "home_url": reverse("home"),
    }
    secondary_url_name = context.pop("secondary_url_name", None)
    if secondary_url_name:
        context["secondary_url"] = reverse(secondary_url_name)
    return render(request, "errors/error.html", context, status=status_code)


def bad_request(request, exception=None):
    return _render_error(request, 400)


def permission_denied(request, exception=None):
    return _render_error(request, 403)


def page_not_found(request, exception=None):
    return _render_error(request, 404)


def server_error(request):
    return _render_error(request, 500)
