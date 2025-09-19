from django import forms
from .models import Prescription
from ckeditor.widgets import CKEditorWidget





class ReceptionBookingForm(forms.ModelForm):

    class Meta:
        model = Prescription
        fields = [
            'clinic',
            'doctor',
            'booking_status',
            'booking',
            'notes',

        ]
        widgets = {
              'notes': CKEditorWidget(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        rich_fields = ['notes']
        for field in self.fields:
           if field not in rich_fields:
            self.fields[field].widget.attrs.update({

            'class': 'form-group',
            'value': field,
            'placeholder': field,
            'style': (
                'width: 98%;'
                'border-radius: 8px;'
                'resize: none;'
                'color: #001100;'
                'height: 40px;'
                'border: 1px solid #414141;'
                'background-color: transparent;'
                'font-family: inherit;'

                ),

            })

