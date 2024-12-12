# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('meetings/', include('meetings.urls')),
    path('', lambda request: redirect('meeting_list')),  # Redirects root URL to the meeting list
]
