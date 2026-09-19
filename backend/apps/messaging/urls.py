from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("man/<int:pk>/", views.thread, name="thread"),
]
