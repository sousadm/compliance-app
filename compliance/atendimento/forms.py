from django import forms

from compliance.atendimento.models import AtendimentoOcorrencia, Atendimento
from compliance.core.models import MODULO_CHOICE


class AtendimentoOcorrenciaForm(forms.ModelForm):
    class Meta:
        model = AtendimentoOcorrencia
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AtendimentoOcorrenciaForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['descricao'].widget.attrs['autofocus'] = True


class AtendimentoForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AtendimentoForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['descricao'].widget.attrs['autofocus'] = True


# class AtendimentoListForm(forms.Form):
#     descricao = forms.CharField(label='Pesquisa', required=False)
#     modulo = forms.ChoiceField(label='Módulo', choices=MODULO_CHOICE, required=False)
#
#     def __init__(self, *args, **kwargs):
#         super(AtendimentoListForm, self).__init__(*args, **kwargs)
#         instance = getattr(self, 'instance', None)
#         if instance:
#             self.fields['descricao'].widget.attrs['autofocus'] = True
