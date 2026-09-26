from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("unlock/<int:pk>/", views.start_unlock, name="unlock"),
    path("chat/<int:pk>/", views.start_chat, name="chat"),
    path("status/<str:order_id>/", views.payment_status, name="status"),
    path("status/<str:order_id>/demo/", views.demo_confirm, name="demo_confirm"),
    path("snippe/webhook/", views.snippe_webhook, name="webhook"),
]
