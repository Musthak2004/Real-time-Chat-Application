from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class SignUpForm(UserCreationForm):

    class Meta:

        model = CustomUser

        fields = (
            "username",
            "email",
            "phone_number",
            "profile_picture",
            "bio",
            "date_of_birth",
        )


class ProfileUpdateForm(forms.ModelForm):

    class Meta:

        model = CustomUser

        fields = (
            "username",
            "phone_number",
            "profile_picture",
            "bio",
            "date_of_birth",
        )