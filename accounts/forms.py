from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe # to add labels in forms
from django.utils.translation import gettext, gettext_lazy as _

from .models import *
from eli.settings import DOMAIN_LIST as DOMAIN_LIST



class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = UserProfile
        fields = ("email", "name",  "gender", "password1", "password2")

    def __init__(self, *args, **kwargs):
        email = kwargs.pop('email')
        print('emailllsllsl', email)
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        #self.fields['email']=forms.EmailField(widget=forms.EmailInput({'placeholder':email}))
        self.fields['email'].widget.attrs['readonly'] = True

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        return email
    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        print('in user save')
        if commit:
            user.save()
            print('saved',user)
        return user


class EmailCodeForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if not proper_email(email):
            msg = "Valid email addresses contain: "
            for d in DOMAIN_LIST:
                msg += d + ' + '
            msg = msg[:-3] + '.'
            msg += " Please use one of those."
            raise forms.ValidationError(msg)
        check_unique = UserProfile.objects.filter(email__iexact=email)
        if len(check_unique) > 0:
            raise ValidationError('That email already exists. Get admin help to recover a forgotten account.')
        return email
    
    def get_email(self):
        return self.cleaned_data.get("email").lower()

class ForgotPasswordForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.CharField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if proper_email(email) and not UserProfile.is_user(email):
            msg = "You are not registered. <br>"
            msg += "Press Cancel and then Sign Up"
            msg += "You can change your password in your profile."
            msg = _(mark_safe(msg))
            raise ValidationError(msg)
        if not UserProfile.is_user(email):
            msg = "This is not a valid email. "
            raise ValidationError(msg)
        return email

class MailForm(forms.Form):
    choices = [
        ('Referee', 'Referee'),
        ('Captain', 'Captain'),
        ('Player', 'Player'),
        ('All', 'All')
    ]

    class Meta:
        fields = ['group', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        super(MailForm, self).__init__(*args, **kwargs)
        self.fields['group'] = forms.ChoiceField(choices=self.choices, required=True)
        self.fields['subject'] = forms.CharField(
            max_length=60,
            widget=forms.Textarea(attrs={'cols': 50, 'rows': 1})
        )
        self.fields['message'] = forms.CharField(
            max_length=5000,
            widget=forms.Textarea(attrs={"rows": 12, "cols": 50, "class": "answer"}),
        )

class PasswordForm(forms.Form):

    class Meta:
        fields = ['email', 'password', 'password_again',]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.CharField(initial=user.email)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['password'] = forms.CharField(required=True) 
        self.fields['password'].widget = forms.PasswordInput(attrs={'placeholder': ''})
        self.fields['password'].label = "Password"
        self.fields['password_again'] = forms.CharField(required=True) 
        self.fields['password_again'].widget = forms.PasswordInput(attrs={'placeholder': ''})
        self.fields['password_again'].label = 'Password again'

    def clean(self):
        password_again = self.cleaned_data.get("password_again")
        password = self.cleaned_data.get("password")
        if password != password_again:
            errmsg = 'Passwords do not match. Please enter <b>BOTH</b> again. '
            raise ValidationError(_(mark_safe(errmsg)))
        validate_password(password) # this test the system specifications of a password given in settings.py

def proper_email(email):
    try:
        domain = email.split('@')[1].lower()
    except IndexError:
        return False
    if domain in DOMAIN_LIST:
        return True
    return False


class VerifyCodeForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(VerifyCodeForm, self).__init__(*args, **kwargs)
        self.secretCode = request.session['code']

    def clean_code(self):
        code = self.cleaned_data.get('code')
        code = code.upper()
        if len(code) != 6 or code != self.secretCode:
            msg = ("Incorrect code: double check email")
            raise ValidationError(msg)
        return code

