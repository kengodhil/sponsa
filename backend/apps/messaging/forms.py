from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Andika ujumbe wako wa kwanza...",
                    "maxlength": 1000,
                }
            )
        }
        labels = {"body": "Ujumbe wako"}
