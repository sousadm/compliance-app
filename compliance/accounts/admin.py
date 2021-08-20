from compliance.accounts.models import User, CategoriaSAC
from django.contrib import admin


class SACCategoriaAdmin(admin.ModelAdmin):
    list_display = ['descricao']
    search_fields = ['descricao']


class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'name']
    search_fields = ['username', 'name']


admin.site.register(CategoriaSAC, SACCategoriaAdmin)
admin.site.register(User, UsuarioAdmin)
