from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from compliance.core.models import Cliente
from compliance.pessoa.forms import ContatoForm
from compliance.pessoa.models import Contato


def contato_render(request, contato):
    context = {}
    lista = Contato.objects.filter(cliente=contato.cliente)
    form = ContatoForm(request.POST or None, instance=contato)
    template_name = 'pessoa/contato.html'
    try:
        if request.POST.get('btn_salvar'):
            form.save()
            return HttpResponseRedirect(reverse('url_cliente_contato', kwargs={'pk': contato.cliente.pk}))

    except Exception as e:
        messages.error(request, e)

    context['cliente'] = contato.cliente
    context['form'] = form
    context['lista'] = lista
    return render(request, template_name, context)


@login_required(login_url='login')
def ClienteContatoView(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    contato = Contato()
    contato.cliente = cliente
    return contato_render(request, contato)


@login_required(login_url='login')
def ContatoView(request, pk):
    contato = Contato.objects.get(pk=pk)
    return contato_render(request, contato)


@login_required(login_url='login')
def ContatoRemoveView(request, pk):
    try:
        contato = Contato.objects.get(pk=pk)
        cliente_pk = contato.cliente.pk
        contato.delete()
    except Exception as e:
        messages.error(request, e)
    return HttpResponseRedirect(reverse('url_cliente_contato', kwargs={'pk': cliente_pk}))
