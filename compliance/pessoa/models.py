from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.
from compliance.core.models import Cliente

LISTA_MES = [
    (1, 'Janeiro'),
    (2, 'Fevereiro'),
    (3, 'Março'),
    (4, 'Abril'),
    (5, 'Maio'),
    (6, 'Junho'),
    (7, 'Julho'),
    (8, 'Agosto'),
    (9, 'Setembro'),
    (10, 'Outubro'),
    (11, 'Novembro'),
    (12, 'Dezembro'),
]


class Contato(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, on_delete=models.CASCADE)
    nome = models.CharField('Nome', max_length=100)
    celular = models.CharField('Celular', max_length=20, null=True)
    email = models.EmailField('E-mail', blank=True, null=True)
    mes = models.IntegerField('Mês', null=True, choices=LISTA_MES)
    dia = models.IntegerField('Dia', default=1, validators=[MaxValueValidator(31), MinValueValidator(1)])

    objects = models.Manager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'contato'
        verbose_name_plural = 'contatos'
        db_table = 'contato'
