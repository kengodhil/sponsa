from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("gate/", views.age_gate, name="gate"),
    path("login/", views.PhoneLoginView.as_view(), name="login"),
    path("logout/", views.PhoneLogoutView.as_view(), name="logout"),
    path("join/lady/", views.join_lady, name="join_lady"),
    path("join/sponsor/", views.join_sponsor, name="join_sponsor"),
    path("my-number/", views.my_number, name="my_number"),
]
