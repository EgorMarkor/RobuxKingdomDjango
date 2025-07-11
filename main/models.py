from django.db import models
import string
import random


def generate_referral_code(length: int = 8) -> str:
    """Return a simple random referral code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


class UserProfile(models.Model):
    username = models.CharField(max_length=1000, verbose_name="Имя")
    balance = models.CharField(max_length=100, verbose_name="Баланс", default="0")
    account_id = models.CharField(max_length=100, verbose_name="ID аккаунта")
    image_url = models.CharField(max_length=500, verbose_name="Аватарка аккаунта")
    referral_id = models.CharField(
        max_length=1000, blank=True, verbose_name="Код друга"
    )
    referrer = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        verbose_name="Пригласивший",
    )
    referral_code = models.CharField(
        max_length=100,
        verbose_name="Код для друга",
        default=generate_referral_code,
        unique=True,
    )
    places = models.ManyToManyField('Place', related_name='owners', blank=True)
    history_balance = models.CharField(max_length=100, verbose_name="Баланс", default="0")
    reward_vk = models.BooleanField(default=False)
    reward_telegram = models.BooleanField(default=False)
    reward_reviews = models.BooleanField(default=False)
    reward_youtube = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации", null=True)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Gamepass(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="gamepasses"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    price = models.CharField(max_length=100, verbose_name="Цена")

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.name


class Place(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="user_places"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    gamepass = models.ForeignKey(
        Gamepass, on_delete=models.SET_NULL, null=True, blank=True, related_name="places"
    )

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.name


class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    order_id = models.CharField(max_length=100, unique=True)
    account = models.CharField(max_length=1000)
    account_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    robux_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):  # pragma: no cover - representation
        return f"Order {self.order_id}"


class WithdrawalRequest(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="withdrawals"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заявка на вывод"
        verbose_name_plural = "Заявки на вывод"

    def __str__(self):  # pragma: no cover - representation
        return f"Withdraw {self.amount} for {self.user}"
