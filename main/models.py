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
    referral_code = models.CharField(
        max_length=100,
        verbose_name="Код для друга",
        default=generate_referral_code,
        unique=True,
    )
    places = models.ManyToManyField('Place', related_name='owners', blank=True)
    history_balance = models.CharField(max_length=100, verbose_name="Баланс", default="0")

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

