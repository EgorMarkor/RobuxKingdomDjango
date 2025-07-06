from django.contrib import admin
from .models import UserProfile, Gamepass, Place


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "balance", "referral_code", "referral_id")
    search_fields = ("username", "referral_code")
    filter_horizontal = ("places",)


@admin.register(Gamepass)
class GamepassAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "user")
    search_fields = ("name",)
    list_filter = ("price",)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "gamepass")
    search_fields = ("name",)
    list_filter = ("gamepass",)
