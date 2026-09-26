from django.urls import path

from . import views

app_name = "staff"

urlpatterns = [
    path("login/", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("sponsor/new/", views.create_profile, name="create_profile"),
    path("sponsor/<int:pk>/edit/", views.edit_profile, name="edit_profile"),
    path("sponsor/<int:pk>/delete/", views.delete_profile, name="delete_profile"),
]
