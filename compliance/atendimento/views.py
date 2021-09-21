from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from compliance.atendimento.forms import AtendimentoOcorrenciaForm, AtendimentoForm
from compliance.atendimento.models import AtendimentoOcorrencia, Atendimento
from compliance.core.models import MODULO_CHOICE, Cliente
from compliance.core.views import get_lista_modulos


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
    context = {}
    atendimento = Atendimento.objects.get(uuid=uuid) if uuid else Atendimento()
    form = AtendimentoForm(request.POST or None, instance=atendimento)
    template_name = 'atendimento/atendimento_edit.html'

    selecionado = request.POST.get('selecionado') or None
    valor = request.POST.get('valor') or ''

    try:
        if request.POST.get('modo_pesquisa'):
            selecionado = None

        if request.POST.get('btn_pesquisar'):
            lista = Cliente.objects.filter(nome__icontains=valor)
            context['lista'] = lista

        if request.POST.get('btn_salvar'):
            form.save()
            return HttpResponseRedirect(reverse('url_atendimento_edit', kwargs={'uuid': atendimento.uuid}))
    except Exception as e:
        messages.error(request, e)
    context['form'] = form
    context['valor'] = valor
    context['selecionado'] = selecionado
    context['atendimento'] = atendimento
    return render(request, template_name, context)
