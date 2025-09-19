from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, SetPasswordForm, \
    PasswordResetForm, UsernameField
from django.utils.translation import gettext_lazy as _
from Accounts.models import User,Profile
from ckeditor.widgets import CKEditorWidget
from doctors.models import Review



class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Confirmation'}),
    )
    extra_kwargs = {"password1": {'write_only': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'bty'),
                'style': (
                    'width:98%;')
            })

    class Meta:
        model = User
        fields = ('email','username','mobile_number',)

        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
            }),
        }


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Email'
    }))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Password'
    }))


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Old Password'
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [

            'first_name',
            'last_name',
            'username',
            'profile_photo',
            'email',
            'mobile_number',
            'national_id',
            'next_of_kin',
            'member_code',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if hasattr(self.instance, name):
                field.initial = getattr(self.instance, name)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-group '),
                'placeholder': field,
                'style': (
                    'width:98%;'
                    'border-radius: 8px;'
                    'resize: none;'
                    'color:  # 001100;'
                    'height: 40px;'
                    'border: 1px solid  # 4141;'
                    'background-color: transparent;'
                    ' font-family: inherit;'

                ),

            })

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [

            'gender',
            'blood_group',
            'country',
            'county',
            'state',
            'postal_code',
            'town_near',
            'allergies',
            'medical_conditions',
            'about',
            'bio',

        ]

        widgets = {'medical_conditions': CKEditorWidget(),}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if hasattr(self.instance, name):
                field.initial = getattr(self.instance, name)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-group '),
                'placeholder': field,
                'style': (
                    'width:98%;'
                    'border-radius: 8px;'
                    'resize: none;'
                    'color:  # 001100;'
                    'height: 40px;'
                    'border: 1px solid  # 4141;'
                    'background-color: transparent;'
                    ' font-family: inherit;'

                ),

            })


   # def save(self, commit=True):
    #    user = super(UserCreationForm, self).save(commit=False)
   #     user.role = "doctor"
  #      if commit:
 #           user.save()
#        return user




class DoctorRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(DoctorRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].label = "First name"
        self.fields["last_name"].label = "Last name"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm your password"

        self.fields["first_name"].widget.attrs.update(
            {
                "placeholder": "Enter first name",
            }
        )
        self.fields["last_name"].widget.attrs.update(
            {
                "placeholder": "Enter last name",
            }
        )
        self.fields["email"].widget.attrs.update(
             {
                "placeholder": "Enter email",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Enter password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Confirm your password",
            }
        )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]
        error_messages = {
            "first_name": {
                "required": "First name is required",
                "max_length": "Name is too long",
            },
            "last_name": {
                "required": "Last name is required",
                "max_length": "Last Name is too long",
            },
        }

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.role = "doctor"
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
     class Meta:
         model = Review
         fields = ["rating", "review"]
         widgets = {
             "rating": forms.Select(attrs={"class": "form-control"}),
             "review": forms.Textarea(
                 attrs={
                     "class": "form-control",
                     "rows": 4,
                     "placeholder": "Write your review here...",
                 }
             ),
         }
