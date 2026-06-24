from django.urls import path, include


urlpatterns = [
    path('conversations/', include('conversations.api.urls')),
]
