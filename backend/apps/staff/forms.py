from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.accounts.phone import normalize_tz_phone, phone_is_valid


class AdminChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Current password", "autocomplete": "current-password"}
        ),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "New password", "autocomplete": "new-password"}
        ),
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm new password", "autocomplete": "new-password"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get("current_password") or ""
        if not self.user.check_password(current):
            raise ValidationError("Current password is incorrect.")
        return current

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1") or ""
        validate_password(password, self.user)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "The two passwords do not match.")
        return cleaned

    def save(self):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.save(update_fields=["password"])
        return self.user


class AdminCreateForm(forms.Form):
    phone = forms.CharField(
        label="Phone number",
        widget=forms.TextInput(
            attrs={
                "placeholder": "07XXXXXXXX",
                "inputmode": "tel",
                "autocomplete": "tel",
            }
        ),
    )
    display_name = forms.CharField(
        label="Display name",
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Admin name"}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "autocomplete": "new-password"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm password", "autocomplete": "new-password"}
        ),
    )

    def clean_phone(self):
        phone = normalize_tz_phone(self.cleaned_data["phone"])
        if not phone_is_valid(phone):
            raise ValidationError(
                "Enter a valid Tanzania mobile number (Vodacom, Airtel, Tigo, Yas, Halotel)."
            )
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already registered.")
        return phone

    def clean_password1(self):
        password = self.cleaned_data.get("password1") or ""
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "The two passwords do not match.")
        return cleaned

    def save(self):
        phone = self.cleaned_data["phone"]
        display_name = (self.cleaned_data.get("display_name") or "").strip()
        if not display_name:
            display_name = f"Admin {phone[-4:]}"
        user = User.objects.create_user(
            phone=phone,
            password=self.cleaned_data["password1"],
            display_name=display_name,
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=False,
            is_adult_confirmed=True,
            is_active=True,
        )
        return user
