import urllib

from django.db import models

# Create your models here.
from compliance.core.models import Cliente, Evento


class Consentimento(models.Model):
    id = models.BigAutoField(primary_key=True)
    autorizado_dt = models.DateTimeField(blank=True, null=True)
    cpf = models.CharField(max_length=11, blank=True, null=True)
    nome = models.CharField(max_length=100, blank=True, null=True)
    arquivo = models.CharField(max_length=250, blank=True, null=True)
    created_dt = models.DateTimeField(blank=True, null=True)
    documento = models.TextField(blank=True, null=True)
    hashcode = models.CharField(max_length=32, blank=True, null=True)
    revogacao_dt = models.DateTimeField(blank=True, null=True)
    updated_dt = models.DateTimeField(blank=True, null=True)
    cliente = models.ForeignKey(Cliente, models.DO_NOTHING, blank=True, null=True)
    anonimizacao_dt = models.DateTimeField(blank=True, null=True)
    autorizador = models.CharField(max_length=32, blank=True, null=True)
    arquivo = models.TextField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'consentimento'

    @property
    def url_arquivo(self):
        return urllib.parse.quote_plus(self.arquivo)


class Tratamento(models.Model):
    id = models.BigAutoField(primary_key=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=252, blank=True, null=True)
    opcao = models.CharField(max_length=100, blank=True, null=True)
    protocolo = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    prazo_dt = models.DateTimeField(null=True)
    encerramento_dt = models.DateTimeField(null=True)
    consentimento = models.ForeignKey(Consentimento, models.DO_NOTHING, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'tratamento'


class TratamentoEvento(models.Model):
    tratamento = models.ForeignKey(Tratamento, models.DO_NOTHING, blank=True, null=True)
    evento = models.ForeignKey(Evento, models.DO_NOTHING, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'tratamento_evento'


class ConsentimentoEvento(models.Model):
    consentimento = models.ForeignKey(Consentimento, models.DO_NOTHING, blank=True, null=True)
    evento = models.ForeignKey(Evento, models.DO_NOTHING, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'consentimento_evento'
