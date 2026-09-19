from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("unlock/<int:pk>/", views.start_unlock, name="unlock"),
    path("listing/", views.start_listing, name="listing"),
    path("status/<str:order_id>/", views.payment_status, name="status"),
    path("status/<str:order_id>/demo/", views.demo_confirm, name="demo_confirm"),
    path("selcom/webhook/", views.selcom_webhook, name="webhook"),
]
