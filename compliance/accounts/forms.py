from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model

from compliance.accounts.models import User
from compliance.core.mail import send_mail_template
from compliance.core.models import Tarefa, Cliente


class RegisterForm(forms.ModelForm):
    User = get_user_model()

    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Confirmação de Senha', widget=forms.PasswordInput
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('A confirmação não está correta')
        return password2

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'autofocus': 'autofocus'})
        }


class SacForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['solicitante', 'celular', 'email', 'categoria_sac', 'demanda']
        widgets = {
            'demanda': forms.Textarea(attrs={'rows': 3}),
            'solicitante': forms.TextInput(attrs={'autofocus': 'autofocus'})
        }

    def __init__(self, *args, **kwargs):
        super(SacForm, self).__init__(*args, **kwargs)
        # self.fields['email'].required = False


class EditAccountForm(forms.ModelForm):
    user_log = get_user_model()

    class Meta:
        model = User
        fields = ['username', 'email', 'celular', 'name', 'is_adm', 'is_fin', 'is_sup', 'is_des', 'is_sac', 'is_staff']

    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            if instance.id:
                self.fields['username'].widget.attrs['readonly'] = True
                self.fields['email'].widget.attrs['autofocus'] = True
            else:
                self.fields['username'].widget.attrs['autofocus'] = True


class ContatoForm(forms.Form):
    nome = forms.CharField(max_length=100, label='Nome')
    email = forms.EmailField(max_length=254, label='E-mail')
    celular = forms.CharField(max_length=20, label='Celular', required=False)
    mensagem = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Mensagem',
    )

    def send_mail(self):
        subject = 'Contato: ' + self.cleaned_data['nome']
        context = {
            'nome': self.cleaned_data['nome'],
            'email': self.cleaned_data['email'],
            'celular': self.cleaned_data['celular'],
            'mensagem': self.cleaned_data['mensagem']
        }
        template_name = 'accounts/email_password.html'
        send_mail_template(
            subject,
            template_name,
            context,
            [settings.CONTACT_EMAIL]
        )


class SerieForm(forms.Form):
    vencimento = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    # serie = forms.CharField(required=False)
