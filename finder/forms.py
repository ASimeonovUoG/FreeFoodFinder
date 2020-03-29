from django import forms
from finder.models import UserAccount, OwnerAccount, Business
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserChangeForm
User = get_user_model()


class NonstickyEmailInput(forms.EmailInput):
    '''Custom email input widget that's "non-sticky"
    (i.e. does not remember submitted values).
    '''
    def get_context(self, name, value, attrs):
        value = None  # Clear the submitted value.
        return super().get_context(name, value, attrs)


class UserForm(forms.ModelForm):
    email = forms.CharField(
        label="", widget=NonstickyEmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    isOwner = forms.BooleanField(widget=forms.HiddenInput(),
                                 initial="False",
                                 required=False)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ('reservation', )


class UserLoginForm(forms.ModelForm):
    email = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )

    # Override so we raise errors if the user login is bad or inactive
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError(
                "Sorry, that login was invalid. Please try again.")
        elif not user.is_active:
            raise forms.ValidationError(
                "Sorry, that login is expired. Please register again.")
        return self.cleaned_data

    # Create a method which will use the cleaned data and login for us
    def login(self, request):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        return user


class Update_form(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', )


class BusinessForm(forms.ModelForm):
    BusinessName = forms.CharField()
    Address = forms.CharField()
    Description = forms.CharField()
    Open = forms.CharField()
    OffersUntil = forms.TimeField()
    Tags = forms.CharField()

    class Meta:
        model = Business
        fields = ('BusinessName', 'Address', 'Description', 'Open',
                  'OffersUntil', 'Tags')
