from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("phone", "display_name", "role", "city", "age", "is_active", "date_joined")
    list_filter = ("role", "city", "is_staff", "is_active")
    search_fields = ("phone", "display_name", "looking_for")
    ordering = ("-date_joined",)
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Profile", {"fields": ("display_name", "role", "city", "age", "looking_for", "is_adult_confirmed")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "display_name", "role", "password1", "password2"),
            },
        ),
    )
