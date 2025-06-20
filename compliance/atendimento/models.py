import uuid
from django.db import models
from django.forms import model_to_dict
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from compliance.core.models import MODULO_CHOICE
from compliance.pessoa.models import Contato
from compliance.accounts.models import User


class AtendimentoOcorrencia(models.Model):
    uuid = models.UUIDField(_("UUID"), editable=False, default=uuid.uuid4)
    descricao = models.CharField('Descrição', max_length=100)

    objects = models.Manager()

    class Meta:
        db_table = 'ocorrencia'

    def __str__(self):
        return self.descricao

    def json(self):
        return model_to_dict(self)

    def get_absolute_url(self):
        return reverse("url_ocorrencia_edit", kwargs={"uuid": self.uuid})


class Atendimento(models.Model):
    uuid = models.UUIDField(_("UUID"), editable=False, default=uuid.uuid4)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    contato = models.ForeignKey(Contato, null=True, on_delete=models.CASCADE)
    ocorrencia = models.ForeignKey(AtendimentoOcorrencia, null=True, on_delete=models.CASCADE)
    modulo = models.CharField('Módulo', max_length=30, choices=MODULO_CHOICE, null=True)
    descricao = models.CharField('Descrição', max_length=100)
    solicitante = models.CharField('Solicitante', max_length=100, null=True)
    observacao = models.TextField('Observação', null=True)
    previsao_dt = models.DateTimeField('Previsão inicio', auto_now_add=True)
    inicio_dt = models.DateTimeField('Inicio', null=True)
    termino_dt = models.DateTimeField('Término', null=True)
    created_dt = models.DateTimeField('Criado em', auto_now_add=True)
    updated_dt = models.DateTimeField('Modificado em', auto_now=True, null=True)

    objects = models.Manager()

    class Meta:
        db_table = 'atendimento'

    def __str__(self):
        return self.descricao

    # def __init__(self):
    #     self.previsao_dt = datetime.now()

    def json(self):
        dados = model_to_dict(self)
        return dados

    def get_absolute_url(self):
        return reverse("url_atendimento_edit", kwargs={"uuid": self.uuid})
