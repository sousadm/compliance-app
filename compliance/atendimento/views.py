import json
from datetime import datetime, date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.dateformat import DateFormat

from compliance.accounts.models import User
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


def atendimento_render(request, uuid=None):
    template_name = 'atendimento/atendimento_edit.html'
    atendimento = Atendimento.objects.get(uuid=uuid) if uuid else Atendimento()
    if not atendimento.pk:
        atendimento.previsao_dt = datetime.today()

    lista_ocorrencia = AtendimentoOcorrencia.objects.all()
    lista = request.POST.get('lista') or []
    valor = request.POST.get('valor') or ''
    selecionado = request.POST.get('selecionado') or None
    if request.POST.get('codigo_pesquisado') and request.POST.get('codigo_pesquisado') != 'None':
        cliente = Cliente.objects.get(pk=int(request.POST.get('codigo_pesquisado')))
    elif atendimento.contato:
        cliente = Cliente.objects.get(pk=atendimento.contato.cliente.pk)
        selecionado = cliente.pk
    else:
        cliente = Cliente()

    # desmembrar este trecho
    if not atendimento.usuario:
        atendimento.usuario = request.user
    if request.POST.get('contato'):
        atendimento.contato = Contato.objects.get(pk=request.POST.get('contato'))
    if request.POST.get('ocorrencia'):
        atendimento.ocorrencia = AtendimentoOcorrencia.objects.get(pk=request.POST.get('ocorrencia'))
    if request.POST.get('modulo'):
        atendimento.modulo = request.POST.get('modulo')
    if request.POST.get('descricao'):
        atendimento.descricao = str(request.POST.get('descricao')).strip()
    if request.POST.get('observacao'):
        atendimento.observacao = str(request.POST.get('observacao')).strip()
    if request.POST.get('previsao_dt'):
        atendimento.previsao_dt = datetime.strptime(request.POST.get('previsao_dt')[:10], '%Y-%m-%d')

    try:
        if request.POST.get('btn_seleciona'):
            selecionado = request.POST.get('codigo_pesquisado')
            cliente = Cliente.objects.get(pk=selecionado)

        if request.POST.get('modo_pesquisa'):
            selecionado = None

        if request.POST.get('btn_pesquisar'):
            lista = Cliente.objects.filter(nome__icontains=valor)

        if request.POST.get('btn_iniciar'):
            atendimento.inicio_dt = datetime.now()
            atendimento.save()
            return HttpResponseRedirect(reverse('url_atendimento_edit', kwargs={'uuid': atendimento.uuid}))

        if request.POST.get('btn_encerrar'):
            atendimento.termino_dt = datetime.now()
            atendimento.save()
            return HttpResponseRedirect(reverse('url_atendimento_edit', kwargs={'uuid': atendimento.uuid}))

        if request.POST.get('btn_salvar'):
            selecionado = request.POST.get('codigo_pesquisado')
            atendimento.save()
            messages.success(request, 'gravado com sucesso')
            return HttpResponseRedirect(reverse('url_atendimento_edit', kwargs={'uuid': atendimento.uuid}))

    except Exception as e:
        messages.error(request, e)

    context = atendimento.json()
    context['created_dt'] = atendimento.created_dt.strftime('%d/%m/%Y %H:%M:%S') if atendimento.created_dt else ''
    context['updated_dt'] = atendimento.updated_dt.strftime('%d/%m/%Y %H:%M:%S') if atendimento.updated_dt else ''
    context['inicio_dt'] = atendimento.inicio_dt.strftime('%d/%m/%Y %H:%M:%S') if atendimento.inicio_dt else ''
    context['termino_dt'] = atendimento.termino_dt.strftime('%d/%m/%Y %H:%M:%S') if atendimento.termino_dt else ''

    context['cliente'] = cliente or atendimento.contato.cliente
    lista_contato = Contato.objects.filter(cliente=cliente)

    context['lista'] = lista
    context['valor'] = valor
    context['username'] = atendimento.usuario.name
    context['selecionado'] = selecionado
    context['codigo_pesquisado'] = request.POST.get('codigo_pesquisado')
    context['previsao_dt'] = DateFormat(atendimento.previsao_dt).format('Y-m-d')
    context['minimo_dt'] = DateFormat(datetime.today()).format('Y-m-d')
    context['lista_contato'] = lista_contato
    context['lista_ocorrencia'] = lista_ocorrencia
    context['modulo_lista'] = get_lista_modulos_somente()
    context['absolute_url'] = atendimento.get_absolute_url()

    return render(request, template_name, context)
