from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import CITY_CHOICES, User
from .phone import normalize_tz_phone, phone_is_valid

DEMO_ADMIN_ALIASES = {"admin", "staff", "administrator"}
DEMO_ADMIN_PHONE = "255700000001"


class AdultConfirmForm(forms.Form):
    is_adult = forms.BooleanField(
        required=True,
        label="Ninathibitisha nina umri wa miaka 18 au zaidi",
    )


class PhoneAuthForm(AuthenticationForm):
    username = forms.CharField(
        label="Nambari ya simu",
        widget=forms.TextInput(
            attrs={
                "placeholder": "07XXXXXXXX",
                "inputmode": "tel",
                "autocomplete": "tel",
            }
        ),
    )

    def clean_username(self):
        raw = (self.cleaned_data.get("username") or "").strip()
        if raw.lower() in DEMO_ADMIN_ALIASES:
            return DEMO_ADMIN_PHONE
        phone = normalize_tz_phone(raw)
        if not phone_is_valid(phone):
            raise ValidationError("Weka nambari sahihi ya simu ya Tanzania.")
        return phone


class BaseJoinForm(UserCreationForm):
    phone = forms.CharField(
        label="Nambari ya simu",
        widget=forms.TextInput(attrs={"placeholder": "07XXXXXXXX", "inputmode": "tel"}),
    )
    display_name = forms.CharField(label="Jina la kuonyesha", max_length=80)
    city = forms.ChoiceField(choices=CITY_CHOICES, label="Jiji")
    age = forms.IntegerField(min_value=18, max_value=80, label="Umri")
    looking_for = forms.CharField(
        label="Unachotafuta",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Umri, jiji, maisha"}),
    )
    is_adult_confirmed = forms.BooleanField(label="Nina umri wa miaka 18+ na najiunga kwa hiari")

    class Meta:
        model = User
        fields = ("phone", "display_name", "city", "age", "looking_for", "password1", "password2")

    def clean_phone(self):
        phone = normalize_tz_phone(self.cleaned_data["phone"])
        if not phone_is_valid(phone):
            raise ValidationError("Weka nambari sahihi ya simu ya Tanzania (Vodacom, Airtel, Tigo, Yas, Halotel).")
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Nambari hii tayari imesajiliwa.")
        return phone

    def clean_age(self):
        age = self.cleaned_data["age"]
        if age < 18:
            raise ValidationError("Ni watu wazima wa miaka 18 na kuendelea tu wanaoweza kujiunga.")
        return age


class LadyEnterForm(forms.Form):
    phone = forms.CharField(
        label="Nambari ya simu",
        widget=forms.TextInput(
            attrs={
                "placeholder": "07XXXXXXXX",
                "inputmode": "tel",
                "autocomplete": "tel",
            }
        ),
    )
    is_adult_confirmed = forms.BooleanField(label="Nina umri wa miaka 18 au zaidi")

    def clean_phone(self):
        phone = normalize_tz_phone(self.cleaned_data["phone"])
        if not phone_is_valid(phone):
            raise ValidationError("Weka nambari sahihi ya simu ya Tanzania.")
        return phone


class LadyJoinForm(BaseJoinForm):
    looking_for = forms.CharField(
        label="Mapendeleo ya mfadhili",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "mf. 40+, Dar, kusafiri"}),
    )


class SponsorJoinForm(BaseJoinForm):
    looking_for = forms.CharField(
        label="Mapendeleo ya mwanamke",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "mf. 21-32, jiji moja"}),
    )
