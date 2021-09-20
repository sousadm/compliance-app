import uuid
from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from compliance.core.models import MODULO_CHOICE
from compliance.pessoa.models import Contato


class AtendimentoOcorrencia(models.Model):
    uuid = models.UUIDField(_("UUID"), editable=False, default=uuid.uuid4)
    descricao = models.CharField('Descrição', max_length=100)

    objects = models.Manager()

    class Meta:
        db_table = 'ocorrencia'

    def __str__(self):
        return self.descricao

    def get_absolute_url(self):
        return reverse("url_ocorrencia_edit", kwargs={"uuid": self.uuid})


class Atendimento(models.Model):
    uuid = models.UUIDField(_("UUID"), editable=False, default=uuid.uuid4)
    contato = models.ForeignKey(Contato, null=True, on_delete=models.CASCADE)
    ocorrencia = models.ForeignKey(AtendimentoOcorrencia, null=True, on_delete=models.CASCADE)
    modulo = models.CharField('Módulo', max_length=30, choices=MODULO_CHOICE, null=True)
    descricao = models.CharField('Descrição', max_length=100)
    observacao = models.TextField('Observação')
    previsao_dt = models.DateTimeField('Previsão inicio')
    inicio_dt = models.DateTimeField('Inicio')
    termino_dt = models.DateTimeField('Término')
    created_dt = models.DateTimeField('Criado em', auto_now_add=True)
    updated_dt = models.DateTimeField('Modificado em', auto_now=True, null=True)

    objects = models.Manager()

    class Meta:
        db_table = 'atendimento'

    def __str__(self):
        return self.descricao

    def get_absolute_url(self):
        return reverse("url_atendimento_edit", kwargs={"uuid": self.uuid})
