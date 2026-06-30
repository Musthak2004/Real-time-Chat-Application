from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    UpdateView,
)

from .forms import (
    SignUpForm,
    ProfileUpdateForm,
)

from .models import CustomUser


class SignUpView(SuccessMessageMixin, CreateView):

    model = CustomUser

    form_class = SignUpForm

    template_name = "registration/signup.html"

    success_url = reverse_lazy("pages:home")

    success_message = "Account created successfully. Welcome!"

    def form_valid(self, form):

        response = super().form_valid(form)

        login(
            self.request,
            self.object
        )

        return response


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = CustomUser

    form_class = ProfileUpdateForm

    template_name = "accounts/profile_update.html"

    success_url = reverse_lazy("pages:home")

    success_message = "Profile updated successfully."

    def get_object(self):

        return self.request.user