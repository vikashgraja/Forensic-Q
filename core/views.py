from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect

from .modules import get_discovered_modules


@csrf_protect
def portal_login_view(request):
    """
    Master Portal Password Login View.
    Authenticates investigative access using only a portal password key.
    """
    next_url = request.GET.get("next") or request.POST.get("next") or "/"

    # Sanitize next_url against open redirect
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = "/"

    # If already logged in, redirect straight away
    if request.session.get("portal_authenticated", False):
        return redirect(next_url)

    error = None

    if request.method == "POST":
        password = request.POST.get("password", "").strip()
        expected_password = getattr(settings, "PORTAL_ACCESS_PASSWORD", "")

        if password and expected_password and password == expected_password:
            request.session["portal_authenticated"] = True
            request.session.modified = True
            return redirect(next_url)
        else:
            error = "Invalid portal access key. Please verify your credentials."

    return render(
        request,
        "core/login.html",
        {
            "error": error,
            "next": next_url,
        },
    )


def portal_logout_view(request):
    """
    Logout View to lock the workstation and clear session credentials.
    """
    request.session.flush()
    return redirect("/login/")


def landing_view(request):
    """
    ForensiQ Landing Page dynamically loading all modules from apps/ directory.
    """
    modules = get_discovered_modules()
    return render(
        request,
        "core/landing.html",
        {
            "modules": modules,
            "total_modules": len(modules),
        },
    )
