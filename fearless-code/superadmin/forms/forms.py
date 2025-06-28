import os
from django import forms
from django.contrib.postgres.fields import IntegerRangeField
from authentication.models import Language
from superadmin.models import Resources
from psycopg2.extras import NumericRange
from django.utils.safestring import mark_safe

class ResourcesForm(forms.ModelForm):
    class Meta:
        model = Resources
        fields = ["name", "type", "file", "link", "thumbnail"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
            "link": forms.TextInput(attrs={"class": "form-control"}),
            "thumbnail": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(ResourcesForm, self).__init__(*args, **kwargs)

        # Show file link
        if self.instance and self.instance.pk and self.instance.file:
            file_url = self.instance.file.url
            file_name = os.path.basename(self.instance.file.name)
            self.fields["file"].help_text = mark_safe(
                f'<br><a href="{file_url}" target="_blank">View: {file_name}</a>'
            )

        # Show thumbnail preview
        if self.instance and self.instance.pk and self.instance.thumbnail:
            thumb_url = self.instance.thumbnail.url
            self.fields["thumbnail"].help_text = mark_safe(
                f'<br><img src="{thumb_url}" alt="Thumbnail" height="100">'
            )
            
            
            
class LanguagesForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ["code", "name"]

        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }