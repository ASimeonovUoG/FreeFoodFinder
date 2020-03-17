from django import forms
from finder.models import UserAccount, OwnerAccount
from django.contrib.auth import get_user_model
User = get_user_model()

class UserForm(forms.ModelForm):
    email = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email','password',)

class UserAccountForm(forms.ModelForm):
    class Meta:
        model = UserAccount 
        fields = ('reservation',)

class UserLoginForm(forms.ModelForm):
    email = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('email','password',)