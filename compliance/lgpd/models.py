from django.db import models

# Create your models here.
from compliance.core.models import Cliente, Evento


class Consentimento(models.Model):
    id = models.BigAutoField(primary_key=True)
    autorizado_dt = models.DateTimeField(blank=True, null=True)
    cpf = models.CharField(max_length=11, blank=True, null=True)
    nome = models.CharField(max_length=100, blank=True, null=True)
    created_dt = models.DateTimeField(blank=True, null=True)
    documento = models.TextField(blank=True, null=True)
    hashcode = models.CharField(max_length=32, blank=True, null=True)
    revogacao_dt = models.DateTimeField(blank=True, null=True)
    updated_dt = models.DateTimeField(blank=True, null=True)
    cliente = models.ForeignKey(Cliente, models.DO_NOTHING, blank=True, null=True)
    anonimizacao_dt = models.DateTimeField(blank=True, null=True)
    autorizador = models.CharField(max_length=32, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'consentimento'


class ConsentimentoEvento(models.Model):
    consentimento = models.ForeignKey(Consentimento, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        db_table = 'consentimento_evento'


class Tratamento(models.Model):
    id = models.BigAutoField(primary_key=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=252, blank=True, null=True)
    opcao = models.CharField(max_length=100, blank=True, null=True)
    protocolo = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    consentimento = models.ForeignKey(Consentimento, models.DO_NOTHING, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'tratamento'
