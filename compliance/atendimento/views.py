from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from compliance.atendimento.forms import AtendimentoOcorrenciaForm, AtendimentoForm
from compliance.atendimento.models import AtendimentoOcorrencia, Atendimento


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


def atendimento_render(request, uuid):
    atendimento = Atendimento.objects.get(uuid=uuid) if uuid else Atendimento()
    form = AtendimentoForm(request.POST or None, instance=atendimento)
    template_name = 'atendimento/atendimento.html'
    try:
        if request.POST.get('btn_salvar'):
            form.save()
            return HttpResponseRedirect(reverse('url_atendimento_edit', kwargs={'uuid': atendimento.uuid}))
    except Exception as e:
        messages.error(request, e)
    lista = AtendimentoOcorrencia.objects.all()
    context = {
        'form': form,
        'atendimento': atendimento,
        'lista': lista
    }
    return render(request, template_name, context)
