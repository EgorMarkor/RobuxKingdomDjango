from django.urls import path
from .views import (
    HomeView,
    BonusView,
    AccountView,
    logout_view,
    CheckAccountView,
    CheckPlace,
    GamePass,
    Buy,
    WithdrawView,
    create_withdraw_request,
    create_order,
    freekassa_notify,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('bonus/', BonusView.as_view(), name='bonus'),
    path('account/', AccountView.as_view(), name='account'),
    path('logout/', logout_view, name="logout"),
    path('check_acc/', CheckAccountView.as_view(), name="CheckAcc"),
    path('places/', CheckPlace.as_view(), name="places"),
    path('gamepasses/', GamePass.as_view(), name="gamepass"),
    path('buy/', Buy.as_view(), name="buy"),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('withdraw/request/', create_withdraw_request, name='create_withdraw'),
    path('pay/', create_order, name='create_order'),
    path('freekassa/notify/', freekassa_notify, name='freekassa_notify'),
]
