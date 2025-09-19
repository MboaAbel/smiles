from django import forms
from .models import Blog
from ckeditor.widgets import CKEditorWidget



class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = [

             'soshi_user',
             'blog_id',
             'blog_image',
             'blog_title',
             'blog_subtitle',
             'caption',
         ]

        widgets = {'caption': CKEditorWidget(),}

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
