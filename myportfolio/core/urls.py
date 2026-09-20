from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/profile/', RedirectView.as_view(url='/dashboard/', permanent=True)),
    
    # Clean URL handling
    path('home', views.home),
    path('about', views.home),
    path('experience', views.home),
    path('projects', views.home),
    path('skills', views.home),
    path('contact', views.home),
]