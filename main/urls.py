from django.urls import path
from .views import HomeView, BonusView, AccountView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('bonus/', BonusView.as_view(), name='bonus'),
    path('account/', AccountView.as_view(), name='account')
]
