from django import forms
from .models.doctors import Education,Experience,Specialty
from Accounts.models import User,Profile
from bookings.models import Prescription
from ckeditor.widgets import CKEditorWidget


class DoctorProfileEducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = "__all__"

class DoctorProfileExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = "__all__"


class DoctorProfileSpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = "__all__"

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["symptoms", "diagnosis", "medications", "notes"]
        widgets = {
            "symptoms": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "diagnosis": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "medications": CKEditorWidget(config_name="default"),
            "notes": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }
class DoctorUpdateForm(forms.ModelForm):
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

class DoctorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [

            'registration_number',
            'about',
            'gender',
            'blood_group',
            'country',
            'county',
            'state',
            'postal_code',
            'town_near',
            'allergies',
            'medical_conditions',

        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


