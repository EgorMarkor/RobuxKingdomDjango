from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "robux_head_pc/index.html"
