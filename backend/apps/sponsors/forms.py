from django import forms

from apps.accounts.models import CITY_CHOICES

from .models import SponsorProfile


class SponsorFilterForm(forms.Form):
    city = forms.ChoiceField(
        required=False,
        choices=[("", "Near my city first")] + list(CITY_CHOICES),
    )
    min_age = forms.IntegerField(required=False, min_value=21, max_value=80, initial=21)
    max_age = forms.IntegerField(required=False, min_value=21, max_value=80, initial=65)
    preference = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "travel, dinner, same city"}),
    )


class SponsorProfileForm(forms.ModelForm):
    class Meta:
        model = SponsorProfile
        fields = (
            "public_name",
            "age",
            "city",
            "lifestyle",
            "preference",
            "teaser",
            "full_bio",
            "photo",
        )
        labels = {
            "public_name": "Name",
            "photo": "Photo",
            "teaser": "Short intro",
            "full_bio": "Full profile",
        }
        widgets = {
            "teaser": forms.TextInput(attrs={"placeholder": "Shown before payment"}),
            "full_bio": forms.Textarea(attrs={"rows": 5, "placeholder": "Shown after payment"}),
            "lifestyle": forms.TextInput(attrs={"placeholder": "travel, cars, dinners"}),
            "preference": forms.TextInput(attrs={"placeholder": "22-30, same city"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""


class SponsorUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV file",
        help_text="Columns: public_name,age,city,lifestyle,preference,teaser,full_bio",
    )
