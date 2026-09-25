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
    path('tech-stack/', views.tech_stack, name='tech_stack'),

    # AI Chatbot 'Ash' Endpoints
    path('ai-chat/', views.ai_chat_page, name='ai_chat'),
    path('ai-chat/message/', views.ai_chat_message, name='ai_chat_message'),
    path('ai-chat/reset/', views.ai_chat_reset, name='ai_chat_reset'),
    path('ai-chat/dataset/download/', views.download_dataset, name='download_dataset'),
    
    # Clean URL handling
    path('home', views.home),
    path('about', views.home),
    path('experience', views.home),
    path('projects', views.home),
    path('skills', views.home),
    path('contact', views.home),
]