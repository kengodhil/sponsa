from django import forms

from apps.accounts.models import CITY_CHOICES

from .models import SponsorProfile


class SponsorFilterForm(forms.Form):
    city = forms.CharField(
        required=False,
        label="Location",
        widget=forms.TextInput(attrs={"placeholder": "Search by location..."}),
    )
    min_age = forms.IntegerField(required=False, min_value=21, max_value=80, initial=21, label="Min age")
    max_age = forms.IntegerField(required=False, min_value=21, max_value=80, initial=65, label="Max age")
    preference = forms.CharField(
        required=False,
        label="Preference",
        widget=forms.TextInput(attrs={"placeholder": "travel, food, same city"}),
    )


class SponsorProfileForm(forms.ModelForm):
    """Admin form: photo + profile details only. No CSV."""

    class Meta:
        model = SponsorProfile
        fields = (
            "public_name",
            "gender",
            "age",
            "city",
            "lifestyle",
            "preference",
            "teaser",
            "full_bio",
            "photo",
            "badge",
            "status",
        )
        labels = {
            "public_name": "Name",
            "gender": "Gender",
            "age": "Age",
            "city": "City",
            "lifestyle": "Lifestyle",
            "preference": "Preference",
            "photo": "Photo",
            "teaser": "Short intro (before pay)",
            "full_bio": "Full bio (after unlock)",
            "badge": "Badge",
            "status": "Status",
        }
        widgets = {
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "teaser": forms.TextInput(attrs={"maxlength": 180, "placeholder": "Short line on the card"}),
            "full_bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Full profile after payment"}),
            "lifestyle": forms.TextInput(attrs={"placeholder": "e.g. travel, business"}),
            "preference": forms.TextInput(attrs={"placeholder": "e.g. 25-35, Dar"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""
        self.fields["photo"].required = False
        self.fields["status"].initial = SponsorProfile.Status.LIVE
