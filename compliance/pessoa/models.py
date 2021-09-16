from django.db import models

# Create your models here.
from compliance.core.models import Cliente


class Contato(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, on_delete=models.CASCADE)
    nome = models.CharField('Nome', max_length=100)
    celular = models.CharField('Celular', max_length=20, null=True)
    email = models.EmailField('E-mail', blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'contato'
        verbose_name_plural = 'contatos'
        db_table = 'contato'
