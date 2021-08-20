from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Cliente, Tarefa

# Register your models here.


class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'fone', 'celular']
    search_fields = ['nome', 'celular', 'cnpj']


class TarefaAdmin(admin.ModelAdmin):
    list_display = ['get_nome', 'resumo', 'solicitante', 'celular']
    search_fields = ['resumo', 'solicitante']

    # list_filter = ['empresa.nome']

    def get_nome(self, obj):
        return obj.cliente.nome


admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Tarefa, TarefaAdmin)
admin.site.register(User, UserAdmin)
