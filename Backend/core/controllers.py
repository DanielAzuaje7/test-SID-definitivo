from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic import View # Usaremos Vistas Basadas en Clases (CBV) para orientación a objetos
from django.contrib.auth.mixins import LoginRequiredMixin

class LoginController(View):
    plantilla = 'login.html'

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.plantilla, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('dashboard') 
        return render(request, self.plantilla, {'form': form})

class DashboardController(LoginRequiredMixin, View):
    planitlla = 'dashboard.html'

    def get(self, request):
        datos = {
            'is_admin': request.user.is_staff or request.user.is_superuser,
            'username': request.user.username,
        }
        return render(request, self.planitlla, datos)

class LogoutController(View):
    def get(self, request):
        logout(request)
        return redirect('login')