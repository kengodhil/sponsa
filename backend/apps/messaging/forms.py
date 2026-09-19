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
                    "placeholder": "Write a clear first message...",
                    "maxlength": 1000,
                }
            )
        }
        labels = {"body": "Your message"}
