from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # Your secure login and edit dashboard
    path('', include('core.urls')),
]