from django import forms

from compliance.pessoa.models import Contato


class ContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ('nome', 'celular', 'email', 'mes', 'dia',)

    def __init__(self, *args, **kwargs):
        super(ContatoForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['nome'].widget.attrs['autofocus'] = True
