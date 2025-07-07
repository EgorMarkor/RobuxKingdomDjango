from django.shortcuts import redirect
from django.views.generic import TemplateView

from .models import UserProfile
import requests
import logging

logger = logging.getLogger(__name__)



def check_regional_pricing(gamepass_id: str) -> bool:
    """Return True if regional pricing is enabled for the given gamepass."""
    url = f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass_id}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network issue
        logger.warning("Failed to fetch gamepass info: %s", exc)
        return False

    try:
        data = resp.json()
    except ValueError:  # pragma: no cover - invalid JSON
        logger.warning("Invalid JSON in gamepass info response")
        return False

    return data.get("isRegionalPricingEnabled", False)


def gamepass_exists_for_price(place_id: str, price: int) -> bool:
    """Return True if the place has a gamepass with the specified price."""
    url = f"https://games.roblox.com/v1/games/{place_id}/game-passes"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network issue
        logger.warning("Failed to fetch gamepasses list: %s", exc)
        return False

    try:
        data = resp.json().get("data", [])
    except ValueError:  # pragma: no cover - invalid JSON
        logger.warning("Invalid JSON in gamepasses list response")
        return False

    for item in data:
        try:
            if int(item.get("price", 0)) == price:
                return True
        except (TypeError, ValueError):
            continue

    return False


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
        context["selected_amount"] = self.request.session.get("selected_amount")
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
        context["selected_place_id"] = self.request.session.get("selected_place_id")
        context["selected_gamepass_id"] = self.request.session.get("selected_gamepass_id")
        context["selected_account_id"] = self.request.session.get("selected_account_id")
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
        context["selected_account_id"] = self.request.session.get("selected_account_id")
        return context
    
    
class CheckAccountView(TemplateView):
    template_name = "robux_check_acc_pc/index.html"

    def get(self, request, *args, **kwargs):
        amount = request.GET.get("amount")
        if amount:
            request.session["selected_amount"] = amount
        account_id = request.GET.get("account_id")
        if account_id:
            request.session["selected_account_id"] = account_id
        elif "selected_account_id" not in request.session:
            profile_id = request.session.get("profile_id")
            if profile_id:
                try:
                    profile = UserProfile.objects.get(pk=profile_id)
                    request.session["selected_account_id"] = profile.account_id
                except UserProfile.DoesNotExist:
                    request.session.pop("profile_id", None)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                context["profile"] = UserProfile.objects.get(pk=profile_id)
            except UserProfile.DoesNotExist:  # pragma: no cover - edge case
                self.request.session.pop("profile_id", None)
        context["selected_account_id"] = self.request.session.get("selected_account_id")
        return context
    
    
class GamePass(TemplateView):
    template_name = "robux_gamepasses_pc/index.html"

    def get(self, request, *args, **kwargs):
        place_id = request.GET.get("place_id")
        if place_id:
            request.session["selected_place_id"] = place_id

        gamepass_id = request.GET.get("gamepass_id")
        if gamepass_id:
            request.session["selected_gamepass_id"] = gamepass_id
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                context["profile"] = UserProfile.objects.get(pk=profile_id)
            except UserProfile.DoesNotExist:  # pragma: no cover - edge case
                self.request.session.pop("profile_id", None)
        context["selected_account_id"] = self.request.session.get("selected_account_id")
        place_id = self.request.GET.get("place_id") or self.request.session.get("selected_place_id")
        context["place_id"] = place_id

        selected_amount = self.request.session.get("selected_amount")
        try:
            expected_price = int(selected_amount) if selected_amount else None
        except (TypeError, ValueError):
            expected_price = None

        if place_id and expected_price is not None:
            context["gamepass_exists"] = gamepass_exists_for_price(place_id, expected_price)
        else:
            context["gamepass_exists"] = False
        context["expected_gamepass_price"] = expected_price

        gamepass_id = self.request.session.get("selected_gamepass_id")
        if gamepass_id:
            context["regional_pricing_enabled"] = check_regional_pricing(gamepass_id)
        else:
            context["regional_pricing_enabled"] = False

        return context
    
class CheckPlace(TemplateView):
    template_name = "robux_places_pc/index.html"

    def get(self, request, *args, **kwargs):
        # place selection happens on gamepass page; nothing to store here
        return super().get(request, *args, **kwargs)

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
        context["selected_amount"] = self.request.session.get("selected_amount")
        context["selected_account_id"] = self.request.session.get("selected_account_id")
        context["selected_place_id"] = self.request.session.get("selected_place_id")
        context["selected_gamepass_id"] = self.request.session.get("selected_gamepass_id")

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
            selected_place_id = context.get("selected_place_id")
            if selected_place_id:
                selected_place = next((p for p in places if str(p.get("id")) == str(selected_place_id)), None)
                context["selected_place"] = selected_place
        except requests.RequestException as e:
            logger.error("Failed to fetch ROBLOX places: %s", e)
            context["places"] = []

        return context
    
class Buy(TemplateView):
    template_name = "robux_buy_pc/index.html"

    def get(self, request, *args, **kwargs):
        # place selection happens on gamepass page; nothing to store here
        return super().get(request, *args, **kwargs)

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
        context["selected_amount"] = self.request.session.get("selected_amount")
        context["selected_account_id"] = self.request.session.get("selected_account_id")
        context["selected_place_id"] = self.request.session.get("selected_place_id")
        context["selected_gamepass_id"] = self.request.session.get("selected_gamepass_id")

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
            selected_place_id = context.get("selected_place_id")
            if selected_place_id:
                selected_place = next((p for p in places if str(p.get("id")) == str(selected_place_id)), None)
                context["selected_place"] = selected_place
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
