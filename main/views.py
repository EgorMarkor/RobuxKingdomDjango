from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "robux_head_pc/index.html"


class BonusView(TemplateView):
    template_name = "robux_bonus_pc/index.html"
    
    
class AccountView(TemplateView):
    template_name = "robux_account_pc/index.html"