from django import forms
from finder.models import UserAccount, OwnerAccount, Business
from django.contrib.auth import get_user_model
User = get_user_model()

class UserForm(forms.ModelForm):
    email = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())
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
    businessName = forms.CharField()
    address = forms.CharField()
    description = forms.CharField()
    workingTime = forms.CharField()
    #OffersUntil = forms.
    tags = forms.CharField()

    class Meta:
      model = Business
      fields = ('businessName','address','description','workingTime','tags')  