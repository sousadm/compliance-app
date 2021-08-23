from django import forms
from django.forms import ModelForm

from compliance.core.models import Cliente, Tarefa, PRIORIDADE_CHOICE, Documento

MONITOR_CHOICES = (
    ("", "selecione"),
    ("1", "Backup"),
    ("2", "Acesso"),
)


class MonitorForm(forms.Form):
    inicio = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))


class TarefaReopenForm(forms.Form):
    identificador = forms.CharField(label='Identificador')
    resumo = forms.CharField(label='Resumo')
    motivo = forms.CharField(label='Motivo da reabertura')
    prioridade = forms.ChoiceField(choices=PRIORIDADE_CHOICE, required=False, label='Prioridade')


class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['serie'].widget.attrs['readonly'] = True
            if instance.id:
                self.fields['cnpj'].widget.attrs['readonly'] = True
                self.fields['nome'].widget.attrs['autofocus'] = True
            else:
                self.fields['cnpj'].widget.attrs['autofocus'] = True


class ClienteConsultaForm(ModelForm):
    class Meta:
        model = Cliente
        exclude = ('nivel', 'monitora', 'pode_sms')

    def __init__(self, *args, **kwargs):
        super(ClienteConsultaForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['serie'].widget.attrs['readonly'] = True
            self.fields['cnpj'].widget.attrs['readonly'] = True


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ('arquivo',)


class ClienteAddUser(forms.Form):
    email = forms.EmailField(label='E-mail para contato')
    nome = forms.CharField(label='Nome de usuário')


class TarefaForm(ModelForm):
    class Meta:
        model = Tarefa
        fields = ['solicitante', 'celular', 'email', 'modulo', 'resumo', 'demanda', 'prioridade', 'identificador']
        widgets = {
            'demanda': forms.Textarea(attrs={'rows': 3}),
            'solicitante': forms.TextInput(attrs={'autofocus': 'autofocus'}),
        }

    def __init__(self, *args, **kwargs):
        super(TarefaForm, self).__init__(*args, **kwargs)
        self.fields['celular'].required = False
        self.fields['email'].required = False
        self.fields['identificador'].required = False
        # self.fields['solicitante'].disabled = self.instance.status != 'INICIO'


class TarefaPausaForm(TarefaForm):
    class Meta(TarefaForm.Meta):
        exclude = ('demanda',)
