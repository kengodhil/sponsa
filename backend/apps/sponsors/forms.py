from django import forms

from apps.accounts.models import CITY_CHOICES

from .models import SponsorProfile


class SponsorFilterForm(forms.Form):
    city = forms.ChoiceField(
        required=False,
        choices=[("", "Karibu na jiji langu kwanza")] + list(CITY_CHOICES),
        label="Jiji",
    )
    min_age = forms.IntegerField(required=False, min_value=21, max_value=80, initial=21, label="Umri mdogo")
    max_age = forms.IntegerField(required=False, min_value=21, max_value=80, initial=65, label="Umri mkubwa")
    preference = forms.CharField(
        required=False,
        label="Mapendeleo",
        widget=forms.TextInput(attrs={"placeholder": "kusafiri, chakula, jiji moja"}),
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
            "public_name": "Jina",
            "age": "Umri",
            "city": "Jiji",
            "lifestyle": "Maisha",
            "preference": "Mapendeleo",
            "photo": "Picha",
            "teaser": "Utangulizi mfupi",
            "full_bio": "Wasifu kamili",
        }
        widgets = {
            "teaser": forms.TextInput(attrs={"placeholder": "Inaonekana kabla ya malipo"}),
            "full_bio": forms.Textarea(attrs={"rows": 5, "placeholder": "Inaonekana baada ya malipo"}),
            "lifestyle": forms.TextInput(attrs={"placeholder": "kusafiri, magari, chakula"}),
            "preference": forms.TextInput(attrs={"placeholder": "22-30, jiji moja"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""


class SponsorUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="Faili la CSV",
        help_text="Safu: public_name,age,city,lifestyle,preference,teaser,full_bio",
    )
