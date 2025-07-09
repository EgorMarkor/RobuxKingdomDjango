from django.shortcuts import redirect
from django.views.generic import TemplateView

from .models import UserProfile, WithdrawalRequest, Order
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

    def post(self, request, *args, **kwargs):
        code = request.POST.get("ref_code")
        profile_id = request.session.get("profile_id")
        if code and profile_id:
            try:
                profile = UserProfile.objects.get(pk=profile_id)
                if not profile.referrer:
                    referrer = UserProfile.objects.filter(username=code).first()
                    if referrer and referrer != profile:
                        profile.referrer = referrer
                        profile.referral_id = code
                        profile.save(update_fields=["referrer", "referral_id"])
            except UserProfile.DoesNotExist:
                pass
        return redirect("bonus")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                profile = UserProfile.objects.get(pk=profile_id)
                context["profile"] = profile
                context["referrals"] = profile.referrals.all()
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

import hashlib
import uuid
from decimal import Decimal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


def create_order(request):
    profile_id = request.session.get("profile_id")
    amount = request.session.get("selected_amount")
    if not profile_id or not amount:
        return redirect("home")
    try:
        profile = UserProfile.objects.get(pk=profile_id)
    except UserProfile.DoesNotExist:
        return redirect("home")

    order_id = uuid.uuid4().hex
    sign_str = f"{settings.FREEKASSA_MERCHANT_ID}:{amount}:{settings.FREEKASSA_SECRET_1}:RUB:{order_id}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    email = request.GET.get("email", "")
    ip = request.META.get("REMOTE_ADDR", "")
    pay_url = (
        f"https://pay.fk.money/?m={settings.FREEKASSA_MERCHANT_ID}"
        f"&oa={amount}&o={order_id}&currency=RUB&s={sign}&email={email}&ip={ip}&i=36"
    )

    Order.objects.create(
        user=profile,
        order_id=order_id,
        account=profile.username,
        account_id=profile.account_id,
        amount=Decimal(amount),
        robux_count=int(amount),
    )
    return redirect(pay_url)


@csrf_exempt
def freekassa_notify(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    order_id = request.POST.get("MERCHANT_ORDER_ID")
    amount = request.POST.get("AMOUNT")
    sign = request.POST.get("SIGN")
    expected = hashlib.md5(
        f"{settings.FREEKASSA_MERCHANT_ID}:{amount}:{settings.FREEKASSA_SECRET_2}:{order_id}".encode()
    ).hexdigest()
    if sign != expected:
        return HttpResponse("wrong sign", status=400)
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("order not found", status=404)
    paid = Decimal(amount)
    order.paid_amount = paid
    order.save(update_fields=["paid_amount"])
    if order.user:
        user = order.user
        try:
            balance = int(user.balance)
        except (TypeError, ValueError):
            balance = 0
        bonus = int(order.robux_count * 0.05)
        user.balance = str(balance + order.robux_count + bonus)
        if user.referrer:
            referrer = user.referrer
            try:
                r_balance = int(referrer.balance)
            except (TypeError, ValueError):
                r_balance = 0
            ref_bonus = int(order.robux_count * 0.05)
            referrer.balance = str(r_balance + ref_bonus)
            try:
                hist = int(referrer.history_balance)
            except (TypeError, ValueError):
                hist = 0
            referrer.history_balance = str(hist + ref_bonus)
            referrer.save(update_fields=["balance", "history_balance"])
        user.save(update_fields=["balance"])
    return HttpResponse("YES")


class WithdrawView(TemplateView):
    template_name = "robux_withdraw_pc/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = self.request.session.get("profile_id")
        if profile_id:
            try:
                context["profile"] = UserProfile.objects.get(pk=profile_id)
            except UserProfile.DoesNotExist:
                self.request.session.pop("profile_id", None)
        # Pass the selected place ID from the session so the template can render
        # the chosen place name or identifier. Without this key the template's
        # ``default`` filter would fail to resolve the variable, resulting in a
        # ``VariableDoesNotExist`` exception when rendering the withdraw page.
        context["selected_place_id"] = self.request.session.get("selected_place_id")
        return context


def create_withdraw_request(request):
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return redirect("home")
    try:
        profile = UserProfile.objects.get(pk=profile_id)
    except UserProfile.DoesNotExist:
        return redirect("home")
    try:
        amount = Decimal(profile.balance)
    except (TypeError, ValueError):
        amount = Decimal("0")
    if amount <= 0:
        return redirect("bonus")
    WithdrawalRequest.objects.create(user=profile, amount=amount)
    profile.balance = "0"
    profile.save(update_fields=["balance"])
    return redirect("bonus")

