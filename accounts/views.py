from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoginForm, RegistrationForm


def _safe_next_url(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


@require_http_methods(["GET", "POST"])
def register(request):
    redirect_url = _safe_next_url(request) or reverse("dashboard:home")
    if request.user.is_authenticated:
        return redirect(redirect_url)

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        messages.success(
            request,
            _("Tu cuenta fue creada correctamente. ¡Bienvenido!"),
        )
        return redirect(redirect_url)

    return render(
        request,
        "accounts/register.html",
        {"form": form, "next": _safe_next_url(request)},
    )


@require_http_methods(["GET", "POST"])
def user_login(request):
    redirect_url = _safe_next_url(request) or reverse("dashboard:home")
    if request.user.is_authenticated:
        return redirect(redirect_url)

    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        messages.success(request, _("Has iniciado sesión correctamente."))
        return redirect(redirect_url)

    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": _safe_next_url(request)},
    )


@login_required
@require_POST
def user_logout(request):
    auth_logout(request)
    messages.success(request, _("Tu sesión se cerró correctamente."))
    return redirect("accounts:login")
