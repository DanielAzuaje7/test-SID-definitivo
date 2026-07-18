from django.urls import path
from .controllers import LoginController, DashboardController, LogoutController

urlpatterns = [
    path('login/', LoginController.as_view(), name='login'),
    path('dashboard/', DashboardController.as_view(), name='dashboard'),
    path('logout/', LogoutController.as_view(), name='logout'),
    path('', LoginController.as_view(), name='root'),
]