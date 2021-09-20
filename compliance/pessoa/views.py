import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from datetime import datetime, date
# Create your views here.
from django.urls import reverse

from compliance.core.models import Cliente
from compliance.core.report import render_to_pdf
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


@login_required(login_url='login')
def ImprimirCadastroCliente(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    context = cliente.json()
    context['contatos'] = Contato.objects.filter(cliente=cliente)
    context['datahora'] = datetime.now().strftime('%d/%m/%Y %H:%M')
    pdf = render_to_pdf('pessoa/rel_cadastro_pessoa.html', context)
    return HttpResponse(pdf, content_type='application/pdf')
