from django.urls import path
from .views import HomeView, BonusView, AccountView, logout_view, CheckAccountView, CheckPlace, GamePass

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('bonus/', BonusView.as_view(), name='bonus'),
    path('account/', AccountView.as_view(), name='account'),
    path('logout/', logout_view, name="logout"),
    path('check_acc/', CheckAccountView.as_view(), name="CheckAcc"),
    path('places/', CheckPlace.as_view(), name="places"),
    path('gamepasses/', GamePass.as_view(), name="gamepass")
]
