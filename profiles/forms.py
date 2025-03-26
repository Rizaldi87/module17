from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserProfileForm(forms.ModelForm):
    image = forms.FileField(required=False)  # Tambahkan field gambar dari Profile
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"required": False}),
        required=False,  # <--- Tambahkan ini agar tidak wajib
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

        widgets = {
            "username": forms.TextInput(),
            "email": forms.EmailInput(),
            "first_name": forms.TextInput(),
            "last_name": forms.TextInput(),
            "password": forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        else:
            user.password = User.objects.get(pk=user.pk).password

        if commit:
            if hasattr(user, "profile"):
                user.profile.image = self.cleaned_data["image"]
                user.profile.save()
            user.save()
        return user
