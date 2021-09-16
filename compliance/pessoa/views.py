from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from compliance.core.models import Cliente
from compliance.pessoa.forms import ContatoForm
from compliance.pessoa.models import Contato
# teste

@login_required(login_url='login')
def cliente_contato(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    lista = Contato.objects.filter(cliente=cliente)
    form = ContatoForm(request.POST or None)
    template_name = 'pessoa/contato.html'
    try:
        pass
    except Exception as e:
        messages.error(request, e)
    lista = Contato.objects.filter(cliente_pk=pk)
    context = {
        'cliente': cliente,
        'form': form,
        'lista': lista
    }
    return render(request, template_name, context)
