from django.shortcuts import redirect
from django.views.generic import TemplateView

from .models import UserProfile


class HomeView(TemplateView):
    template_name = "robux_head_pc/index.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        if username:
            profile, _created = UserProfile.objects.get_or_create(username=username)
            request.session["profile_id"] = profile.pk
        return redirect("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                context["profile"] = UserProfile.objects.get(pk=profile_id)
            except UserProfile.DoesNotExist:  # pragma: no cover - edge case
                self.request.session.pop("profile_id", None)
        return context
