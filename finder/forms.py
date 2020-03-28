from django import forms
from finder.models import UserAccount, OwnerAccount, Business
from django.contrib.auth import get_user_model
User = get_user_model()

class UserForm(forms.ModelForm):
    email = forms.CharField(label="",widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label="",widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    isOwner = forms.BooleanField(widget=forms.HiddenInput(), initial="False", required=False)

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
"""
class Update_form(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email','password',)
"""

class BusinessForm(forms.ModelForm):
    BusinessName = forms.CharField()
    Address = forms.CharField()
    Description = forms.CharField()
    Open = forms.CharField()
    #OffersUntil = forms.
    Tags = forms.CharField()
    

    class Meta:
      model = Business
      fields = ('BusinessName','Address','Description','Open','Tags')  