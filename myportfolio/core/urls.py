from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/profile/', RedirectView.as_view(url='/dashboard/', permanent=True)),
    # Catch all the clean section URLs and route them to the home view
    path('home', views.home),
    path('home/', views.home),
    path('about', views.home),
    path('about/', views.home),
    path('experience', views.home),
    path('experience/', views.home),
    path('projects', views.home),
    path('projects/', views.home),
    path('skills', views.home),
    path('skills/', views.home),
    path('contact', views.home),
    path('contact/', views.home),
]