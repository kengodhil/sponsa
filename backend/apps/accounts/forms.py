from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import CITY_CHOICES, User
from .phone import normalize_tz_phone, phone_is_valid


class AdultConfirmForm(forms.Form):
    is_adult = forms.BooleanField(
        required=True,
        label="I confirm I am 18 years or older",
    )


class PhoneAuthForm(AuthenticationForm):
    username = forms.CharField(
        label="Mobile number",
        widget=forms.TextInput(
            attrs={
                "placeholder": "07XXXXXXXX",
                "inputmode": "tel",
                "autocomplete": "tel",
            }
        ),
    )

    def clean_username(self):
        phone = normalize_tz_phone(self.cleaned_data["username"])
        if not phone_is_valid(phone):
            raise ValidationError("Enter a valid Tanzania mobile number.")
        return phone


class BaseJoinForm(UserCreationForm):
    phone = forms.CharField(
        label="Mobile number",
        widget=forms.TextInput(attrs={"placeholder": "07XXXXXXXX", "inputmode": "tel"}),
    )
    display_name = forms.CharField(label="Name to show", max_length=80)
    city = forms.ChoiceField(choices=CITY_CHOICES)
    age = forms.IntegerField(min_value=18, max_value=80)
    looking_for = forms.CharField(
        label="What you prefer",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Age, city, lifestyle"}),
    )
    is_adult_confirmed = forms.BooleanField(label="I am 18+ and join by choice")

    class Meta:
        model = User
        fields = ("phone", "display_name", "city", "age", "looking_for", "password1", "password2")

    def clean_phone(self):
        phone = normalize_tz_phone(self.cleaned_data["phone"])
        if not phone_is_valid(phone):
            raise ValidationError("Enter a valid Tanzania mobile number (Vodacom, Airtel, Tigo, Yas, Halotel).")
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("This number is already registered.")
        return phone

    def clean_age(self):
        age = self.cleaned_data["age"]
        if age < 18:
            raise ValidationError("Only adults 18 years and above can join.")
        return age


class LadyEnterForm(forms.Form):
    phone = forms.CharField(
        label="Mobile number",
        widget=forms.TextInput(
            attrs={
                "placeholder": "07XXXXXXXX",
                "inputmode": "tel",
                "autocomplete": "tel",
            }
        ),
    )
    is_adult_confirmed = forms.BooleanField(label="I am 18 or older")

    def clean_phone(self):
        phone = normalize_tz_phone(self.cleaned_data["phone"])
        if not phone_is_valid(phone):
            raise ValidationError("Enter a valid Tanzania mobile number.")
        return phone


class LadyJoinForm(BaseJoinForm):
    looking_for = forms.CharField(
        label="Sponsor preference",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. 40+, Dar, travel"}),
    )


class SponsorJoinForm(BaseJoinForm):
    looking_for = forms.CharField(
        label="Lady preference",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. 21-32, same city"}),
    )
