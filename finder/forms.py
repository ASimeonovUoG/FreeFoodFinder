
from django import forms
from finder.models import UserAccount, OwnerAccount, Business, Offer
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm
from finder.distance import validate_address
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
        label="", widget=NonstickyEmailInput(attrs={'placeholder': 'Email address'}))
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

    # Override so we raise errors if the user login is bad or inactive
    def validate(self,user):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        try:
            validate_password(user.password,user)
        except ValidationError as ve:
            self.add_error('password', ve.messages)
            return False
        return True



class UserAccountForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ('reservation', )


class UserLoginForm(forms.ModelForm):
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Email','autofocus':'autofocus', 'class':'form-control', 'id':'inputemail' }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder': 'Password' , 'class':'form-control', 'id':'inputpassword'}))

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
    #only show the email
    password = None
    class Meta:
        model = User
        fields = ('email', )


class BusinessForm(forms.ModelForm):
    businessName = forms.CharField(required=True, label="Business name")
    address = forms.CharField(required=True, label="Address", validators=[validate_address])
    description = forms.CharField(required=True, label="Description")
    workingTime = forms.CharField(required=True, label="Opening hours")
    offersUntil = forms.TimeField(required=True, label="Offers until")
    tags = forms.CharField(required=True, label="Keywords")
    picture = forms.ImageField(required=False, label="Picture")

    class Meta:
        model = Business
        fields = ('businessName', 'address', 'description', 'workingTime',
                  'offersUntil', 'tags', 'picture')


class OfferForm(forms.ModelForm):
    portionAmount = forms.IntegerField(label="Portion amount")

    class Meta:
        model = Offer
        fields = ('portionAmount',)