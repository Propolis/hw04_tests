from django.shortcuts import render


def csrf_failure(request, reason=""):
    return render(request, "core/custom_handlers/403csrf.html")


def page_not_found(request, exception):
    return render(request, "core/custom_handlers/404.html", {"path": request.path}, status=404)
