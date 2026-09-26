from django.urls import path

from . import views

app_name = "staff"

urlpatterns = [
    path("login/", views.admin_login, name="login"),
    path("", views.dashboard, name="dashboard"),
    path("user/<int:pk>/", views.user_detail, name="user_detail"),
    path("sponsor/new/", views.create_profile, name="create_profile"),
    path("sponsor/<int:pk>/edit/", views.edit_profile, name="edit_profile"),
    path("sponsor/csv/", views.csv_upload, name="csv_upload"),
]
