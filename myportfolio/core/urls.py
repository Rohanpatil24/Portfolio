from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
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