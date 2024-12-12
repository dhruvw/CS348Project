# meetings/urls.py
from django.urls import path, include
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.meeting_list, name='meeting_list'),  # Root URL for the meetings app
    path('new/', views.meeting_create, name='meeting_create'),
    path('<int:pk>/edit/', views.meeting_edit, name='meeting_edit'),
    path('<int:pk>/delete/', views.meeting_delete, name='meeting_delete'),
    path('organizers/', views.organizer_list, name='organizer_list'),
    path('organizers/new/', views.organizer_create, name='organizer_create'),
    path('organizers/<int:pk>/edit/', views.organizer_edit, name='organizer_edit'),
    path('organizers/<int:pk>/delete/', views.organizer_delete, name='organizer_delete'),
    path('report/', views.generate_report, name='generate_report'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
