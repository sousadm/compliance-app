from django import forms


class UploadFileOnlyForm(forms.Form):
    file = forms.FileField(label='Arquivo', max_length=500)

class UploadFileForm(forms.Form):
    title = forms.CharField(label='arquivo', max_length=500)
    file = forms.FileField()
