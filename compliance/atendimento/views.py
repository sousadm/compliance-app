import json
from datetime import datetime, date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.dateformat import DateFormat

from compliance.atendimento.forms import AtendimentoOcorrenciaForm, AtendimentoForm
from compliance.atendimento.models import AtendimentoOcorrencia, Atendimento
from compliance.core.models import MODULO_CHOICE, Cliente
from compliance.core.views import get_lista_modulos, get_lista_modulos_somente
from compliance.pessoa.models import Contato


def ocorrencia_render(request, uuid):
    ocorrencia = AtendimentoOcorrencia.objects.get(uuid=uuid) if uuid else AtendimentoOcorrencia()
    form = AtendimentoOcorrenciaForm(request.POST or None, instance=ocorrencia)
    template_name = 'atendimento/ocorrencia.html'
    try:
        if request.POST.get('btn_aplicar'):
            form.save()
            return HttpResponseRedirect(reverse('url_ocorrencia'))
    except Exception as e:
        messages.error(request, e)
    lista = AtendimentoOcorrencia.objects.all()
    context = {
        'form': form,
        'ocorrencia': ocorrencia,
        'lista': lista
    }
    return render(request, template_name, context)


@login_required(login_url='login')
def ocorrencia(request):
    return ocorrencia_render(request, None)


@login_required(login_url='login')
def ocorrenciaEdit(request, uuid):
    return ocorrencia_render(request, uuid)


@login_required(login_url='login')
def OcorrenciaRemove(request, uuid):
    try:
        ocorrencia = AtendimentoOcorrencia.objects.get(uuid=uuid)
        ocorrencia.delete()
    except Exception as e:
        messages.error(request, e)
    return HttpResponseRedirect(reverse('url_ocorrencia'))


@login_required(login_url='login')
def atendimentoEdit(request, uuid):
    return atendimento_render(request, uuid)


@login_required(login_url='login')
def atendimentoAdd(request):
    return atendimento_render(request)


@login_required(login_url='login')
def atendimentoList(request):
    template_name = 'atendimento/atendimento_list.html'
    lista = Atendimento.objects.all()
    descricao = request.POST.get('descricao') or ''
    modulo = request.POST.get('modulo') or ''
    context = {
        'modulos': get_lista_modulos(),
        'modulo': modulo,
        'descricao': descricao,
        'lista': lista
    }
    return render(request, template_name, context)


def valor_pesquisa(request, pk):
    return pk


def atendimento_render(request, uuid=None):
    atendimento = Atendimento.objects.get(uuid=uuid) if uuid else Atendimento()
    cliente = Cliente.objects.get(pk=atendimento.contato.cliente) if atendimento.contato else Cliente()
    lista_ocorrencia = AtendimentoOcorrencia.objects.all()
    if not atendimento.previsao_dt:
        atendimento.previsao_dt = datetime.now()
    context = atendimento.json()

    lista_contato = []
    template_name = 'atendimento/atendimento_edit.html'

    cliente = request.POST.get('cliente')
    selecionado = request.POST.get('selecionado') or None
    lista = request.POST.get('lista') or []
    valor = request.POST.get('valor') or ''

    try:
        if request.POST.get('btn_seleciona'):
            selecionado = request.POST.get('codigo')
            cliente = Cliente.objects.get(pk=selecionado)

        if request.POST.get('modo_pesquisa'):
            selecionado = None

        if request.POST.get('btn_pesquisar'):
            lista = Cliente.objects.filter(nome__icontains=valor)

        # if request.POST.get('btn_salvar'):
        #     form.save()
        #     return HttpResponseRedirect(reverse('url_atendimento_edit', kwargs={'uuid': atendimento.uuid}))

    except Exception as e:
        messages.error(request, e)

    if cliente:
        lista_contato = Contato.objects.filter(cliente=cliente)

    context['lista'] = lista
    context['valor'] = valor
    context['previsao_dt'] = DateFormat(atendimento.previsao_dt).format('Y-m-d')
    context['cliente'] = cliente
    context['lista_contato'] = lista_contato
    context['lista_ocorrencia'] = lista_ocorrencia
    context['modulo_lista'] = get_lista_modulos_somente()
    context['selecionado'] = selecionado

    return render(request, template_name, context)
