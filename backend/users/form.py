# forms.py
from django import forms
from users.models import CustomUser as User

class UserRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError(
                "Les mots de passe ne sont pas identiques"
            )
        return cleaned_data

class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
    def clean(self):
        if self.is_valid() == False:
            raise forms.ValidationError(
                "identifiant ou mot de passe incorrect"
            )