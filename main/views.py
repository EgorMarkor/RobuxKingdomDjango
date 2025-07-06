from django.shortcuts import redirect
from django.views.generic import TemplateView

from .models import UserProfile
import requests
import logging

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "robux_head_pc/index.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        print(username)
        if username:
            r1 = requests.post(
                'https://users.roblox.com/v1/usernames/users',
                json={"usernames":[username], "excludeBannedUsers":True},
                timeout=5
            )

            d1 = r1.json()['data'][0]
            if 'errorMessage' in d1:
                raise ValueError(d1['errorMessage'])
            user_id = d1['id']

            # 2. Получаем thumbnail
            r2 = requests.get(
                'https://thumbnails.roblox.com/v1/users/avatar-headshot',
                params={
                    'userIds': user_id,
                    'size': '420x420',
                    'format': 'Png',
                    'isCircular': 'false'
                }
            )
            d2 = r2.json()['data'][0]['imageUrl']
            print(d2)

            profile, _created = UserProfile.objects.get_or_create(username=username, account_id=user_id, image_url=d2)
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


class BonusView(TemplateView):
    template_name = "robux_bonus_pc/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                context["profile"] = UserProfile.objects.get(pk=profile_id)
            except UserProfile.DoesNotExist:  # pragma: no cover - edge case
                self.request.session.pop("profile_id", None)
        return context
    
    
class AccountView(TemplateView):
    template_name = "robux_account_pc/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                context["profile"] = UserProfile.objects.get(pk=profile_id)
            except UserProfile.DoesNotExist:  # pragma: no cover - edge case
                self.request.session.pop("profile_id", None)
        return context
    
    
class CheckAccountView(TemplateView):
    template_name = "robux_check_acc_pc/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                context["profile"] = UserProfile.objects.get(pk=profile_id)
            except UserProfile.DoesNotExist:  # pragma: no cover - edge case
                self.request.session.pop("profile_id", None)
        return context
    
    
class GamePass(TemplateView):
    template_name = "robux_gamepasses_pc/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                context["profile"] = UserProfile.objects.get(pk=profile_id)
            except UserProfile.DoesNotExist:  # pragma: no cover - edge case
                self.request.session.pop("profile_id", None)
        return context
    
class CheckPlace(TemplateView):
    template_name = "robux_places_pc/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")

        if not profile_id:
            return context

        try:
            profile = UserProfile.objects.get(pk=profile_id)
        except UserProfile.DoesNotExist:
            self.request.session.pop("profile_id", None)
            return context

        context["profile"] = profile

        # Функция для получения всех плейсов пользователя
        def fetch_roblox_places(account_id):
            places = []
            cursor = ""
            url = f"https://games.roblox.com/v2/users/{account_id}/games"

            while True:
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
                data = resp.json()
                places.extend(data.get("data", []))
                cursor = data.get("nextPageCursor")
                if not cursor:
                    break
                params["cursor"] = cursor

            return places

        try:
            places = fetch_roblox_places(profile.account_id)
            logger.debug("ROBLOX places for account %s: %r", profile.account_id, places)
            context["places"] = places
        except requests.RequestException as e:
            logger.error("Failed to fetch ROBLOX places: %s", e)
            context["places"] = []

        return context
    
def logout_view(request):
    """
    Разлогинивает пользователя, удаляет profile_id из сессии и
    перенаправляет на главную страницу.
    """
    # убираем сохранённый профиль
    request.session.pop('profile_id', None)
    # стандартный logout очистит аутентификацию
    return redirect('home')