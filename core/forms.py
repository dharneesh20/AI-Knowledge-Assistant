from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Document, Feedback


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ("title", "file")


class AskForm(forms.Form):
    query = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Ask anything from your documents...",
            }
        ),
         )
    top_k = forms.IntegerField(min_value=1, max_value=15, initial=5)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Your feedback..."})
        }
