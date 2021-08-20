import json
import re

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.core import validators
from django.db import models
from django.forms import model_to_dict

TRUE_FALSE_CHOICES = (
    (True, 'Sim'),
    (False, 'Não')
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        'Usuário', max_length=30, unique=True,
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'),
                                              'permitido letras, digitos ou os '
                                              'seguintes caracteres: @/./+/-/_', 'invalid')]
    )
    email = models.EmailField('E-mail', unique=True, null=True)
    name = models.CharField('Nome', max_length=100, blank=True)
    celular = models.CharField('Celular', max_length=20, null=True, blank=True)
    is_active = models.BooleanField('Ativo', blank=True, default=True)
    is_staff = models.BooleanField('Administrador', blank=True, default=False)
    date_joined = models.DateTimeField('Data de Entrada', auto_now_add=True)
    is_sac = models.BooleanField('Atendimento SAC', default=False, blank=True)
    is_adm = models.BooleanField('Administrativo', default=False, blank=True)
    is_fin = models.BooleanField('Financeiro', blank=True, default=False)
    is_sup = models.BooleanField('Suporte', blank=True, default=False)
    is_des = models.BooleanField('Desenvolvimento', blank=True, default=False)
    is_consulta = models.BooleanField('Desenvolvimento', blank=True, default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name or self.username

    def json(self):
        obj = model_to_dict(self)
        obj["name"] = self.name
        obj["email"] = self.email
        obj["celular"] = self.celular
        return obj

    def dump(self):
        return json.dumps(self.json())

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return str(self)

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class CategoriaSAC(models.Model):
    descricao = models.CharField('Descrição', max_length=100, blank=True)
    codigo = models.CharField('Código', max_length=10, blank=True)
    is_adm = models.BooleanField('Administrativo', choices=TRUE_FALSE_CHOICES, default=False, blank=True)
    is_fin = models.BooleanField('Financeiro', choices=TRUE_FALSE_CHOICES, blank=True, default=False)
    is_sup = models.BooleanField('Suporte', choices=TRUE_FALSE_CHOICES, blank=True, default=False)
    is_des = models.BooleanField('Desenvolvimento', choices=TRUE_FALSE_CHOICES, blank=True, default=False)
    is_active = models.BooleanField('Em uso', choices=TRUE_FALSE_CHOICES, blank=True, default=True)
    tempo_previsto = models.IntegerField('Tempo previsto em min', null=True)

    objects = UserManager()

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = 'sac_categoria'
        verbose_name = 'Categoria SAC'
        verbose_name_plural = 'Categorias SAC'
