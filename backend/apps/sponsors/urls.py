from django.urls import path

from . import views

app_name = "sponsors"

urlpatterns = [
    path("browse/", views.browse, name="browse"),
    path("man/<int:pk>/", views.profile_detail, name="detail"),
    path("my-card/", views.my_listing, name="my_listing"),
    path("my-card/edit/", views.edit_listing, name="edit_listing"),
]
