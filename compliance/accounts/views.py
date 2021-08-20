from datetime import datetime
from time import timezone

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from compliance.accounts.forms import EditAccountForm, SacForm, SerieForm
from compliance.accounts.models import User, CategoriaSAC
from compliance.accounts.senha import gerar_senha_letras_numeros, gerarNumeroSerie
from compliance.core.mail import send_mail_template
from compliance.core.models import Tarefa, Cliente, TarefaEvento, Evento
from compliance.core.views import addEventoTarefaMsg, TempoDecorrido


@login_required
def dashboard(request):
    template_name = 'accounts/dashboard.html'
    return render(request, template_name)


def logout_view(request):
    logout(request)


@login_required
def SAC_cliente(request, pk):
    tarefa = Tarefa()
    tarefa.modulo = 'SAC'
    tarefa.status = 'INICIO'
    tarefa.user = request.user
    cliente = Cliente.objects.get(pk=pk)
    tarefa.cliente = cliente
    tarefa.email = cliente.email
    tarefa.celular = cliente.celular
    tarefa.solicitante = cliente.contato
    form = SacForm(request.POST or None, instance=tarefa)
    template_name = 'accounts/sac_edit.html'
    try:
        if request.POST:
            res = form.save()
            addEventoTarefaMsg(request, tarefa, 'inclusão de SAC')
            messages.success(request, 'incluido com sucesso')
            return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': res.id or res.pk}))

    except Exception as e:
        messages.error(request, e)

    context = {
        'form': form,
        'tarefa': tarefa,
        'status': tarefa.getStatusSAC(request.user)
    }
    return render(request, template_name, context)


@login_required
def atendimentoSAC(request):
    template_name = 'accounts/sac.html'
    lista = Tarefa.objects.filter(modulo='SAC').order_by('pk').reverse()
    context = {
        'lista': lista
    }
    return render(request, template_name, context)


@login_required
def userEdit(request, pk):
    context = {}
    template_name = 'accounts/edit.html'
    user = User.objects.get(pk=pk)
    form = EditAccountForm(request.POST or None, instance=user)

    if request.method == 'POST':
        try:
            if request.POST.get('btn_ativa') or request.POST.get('btn_staff'):
                if request.POST.get('btn_ativa'):
                    user.is_active = not user.is_active

                if request.POST.get('btn_staff'):
                    user.is_staff = not user.is_staff

                user.save()
                return HttpResponseRedirect(reverse('url_user_edit', kwargs={'pk': user.pk}))

            if form.is_valid():
                user = form.save()
                messages.success(request, 'modificado com sucesso')
                return HttpResponseRedirect(reverse('url_user_edit', kwargs={'pk': user.pk}))

        except Exception as e:
            messages.error(request, e)
            # return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': pk}))

    context['form'] = form
    context['usuario'] = user
    return render(request, template_name, context)


@login_required
def userRegister(request):
    context = {}
    user = User()
    template_mail = 'accounts/email_password.html'
    template_name = 'accounts/edit.html'
    form = EditAccountForm(request.POST or None, instance=user)
    if request.method == 'POST':
        try:
            if form.is_valid():
                user = form.save()

                senha = gerar_senha_letras_numeros(6)
                hasher = PBKDF2PasswordHasher()
                salt = hasher.salt()
                user.password = hasher.encode(senha, salt)
                user.save()

                messages.success(request, 'senha enviada para e-mail')

                context_mail = {
                    'username': user.username,
                    'keyuser': senha,
                    'email': user.email,
                    'mensagem': 'Sr(a): ' + user.name +
                                '\n Segue senha de acesso'
                                '\n Para sua segurança, acesse o sistema e modifique sua senha',
                }
                send_mail_template(
                    'senha de acesso',
                    template_mail,
                    context_mail,
                    [user.email]
                )

                return HttpResponseRedirect(reverse('url_user_edit', kwargs={'pk': user.pk}))

        except Exception as e:
            messages.error(request, e)

    context['form'] = form
    context['usuario'] = user
    return render(request, template_name, context)


@login_required
def SAC_avulso(request):
    tarefa = Tarefa()
    tarefa.user = request.user
    tarefa.modulo = 'SAC'
    tarefa.status = 'INICIO'
    form = SacForm(request.POST or None, instance=tarefa)
    template_name = 'accounts/sac_edit.html'
    try:
        if request.POST:
            res = form.save()
            addEventoTarefaMsg(request, tarefa, 'inclusão de SAC')
            messages.success(request, 'incluido com sucesso')
            return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': res.id or res.pk}))

    except Exception as e:
        messages.error(request, e)

    context = {
        'form': form,
        'tarefa': tarefa,
        'status': tarefa.getStatusSAC(request.user)
    }
    return render(request, template_name, context)


@login_required
def atendimentoEditSAC(request, pk):
    tarefa = Tarefa.objects.get(pk=pk)
    usuario = tarefa.user
    categoria = CategoriaSAC.objects.get(pk=tarefa.categoria_sac.pk)
    form = SacForm(request.POST or None, instance=tarefa)

    readonly = tarefa.user != request.user or tarefa.encerrado_dt

    q_active = Q(is_active=True)
    q_adm = Q(is_adm=True if categoria.is_adm else None)
    q_fin = Q(is_fin=True if categoria.is_fin else None)
    q_sup = Q(is_sup=True if categoria.is_sup else None)
    q_des = Q(is_des=True if categoria.is_des else None)
    usuarios = User.objects.filter(q_active, q_adm | q_fin | q_sup | q_des).exclude(pk=request.user.pk)

    template_name = 'accounts/sac_edit.html'
    try:

        if request.POST.get('btn_email') and tarefa.pk:
            template_mail = 'accounts/email_sac.html'
            context_mail = {
                'numero': tarefa.pk,
                'datahora': tarefa.created_at,
                'solicitante': tarefa.solicitante,
                'email': tarefa.email,
                'celular': tarefa.celular,
                'demanda': tarefa.demanda,
            }
            send_mail_template(
                'SAC - ' + str(tarefa.pk),
                template_mail,
                context_mail,
                [tarefa.email]
            )
            addEventoTarefaMsg(request, tarefa,
                               'sac - ' + str(tarefa.pk) + ' enviado para email ' + tarefa.email)
            messages.success(request, 'atendimento enviado para ' + tarefa.email)
            return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': pk}))

        if not tarefa.ultimo_tempo:
            tarefa.ultimo_tempo = datetime.now()
        tempo = TempoDecorrido(tarefa.ultimo_tempo.astimezone(), datetime.now())

        if request.POST.get('btn_iniciar') or request.POST.get('btn_reiniciar'):
            tarefa.user == request.user
            tarefa.iniciado_dt = datetime.now()
            tarefa.addTempoStatus(tempo, 'PRODUCAO')
            tarefa.save()
            addEventoTarefaMsg(request, tarefa,
                               'atendimento ' + 'iniciado' if request.POST.get('btn_iniciar') else 'reiniciado')
            return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': pk}))

        elif request.POST.get('btn_encaminhar'):
            tarefa.addTempoStatus(tempo, 'PAUSA')
            usuario = User.objects.get(pk=request.POST.get('user_encaminha'))
            tarefa.user = usuario
            tarefa.save()
            addEventoTarefaMsg(request, tarefa, 'SAC encaminhado para ' + tarefa.user.username)
            return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': pk}))

        elif request.POST.get('btn_finalizar'):
            tarefa.addTempoStatus(tempo, 'ENCERRADO')
            tarefa.encerrado_dt = datetime.now()
            tarefa.save()
            addEventoTarefaMsg(request, tarefa, 'SAC encerrado')
            return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': pk}))

        elif request.POST.get('btn_observar'):
            addEventoTarefaMsg(request, tarefa, request.POST.get('observacao'))
            return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': pk}))

        if request.POST and form.is_valid():
            tarefa.save()
            messages.success(request, 'gravado com sucesso')
            return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': pk}))

    except Exception as e:
        messages.error(request, e)
        return HttpResponseRedirect(reverse('url_sac_edit', kwargs={'pk': pk}))

    lista_eventos = TarefaEvento.objects.filter(Q(tarefa=tarefa)).order_by('pk').reverse()

    context = {
        'form': form,
        'tarefa': tarefa,
        'lista_encaminha': usuarios,
        'usuario': usuario,
        'readonly': readonly,
        'status': tarefa.getStatusSAC(request.user),
        'demanda': tarefa.demanda,
        'eventos': lista_eventos
    }
    return render(request, template_name, context)


@login_required(login_url='login')
def encerramento(request):
    if request.user.is_consulta:
        logout(request)
        return HttpResponseRedirect(reverse('home'))

    tarefas = Tarefa.objects.filter(Q(status='PRODUCAO'), Q(encerrado_dt__isnull=True), Q(user=request.user))
    msg = ''
    if request.method == 'POST':
        if request.POST.get('btn_intervalo'):
            msg = 'intervalo de expediente'
        elif request.POST.get('btn_encerramento'):
            msg = 'encerramento de expediente'
        if msg:
            evento = Evento()
            evento.descricao = msg
            evento.user = request.user
            evento.save()
            for tar in tarefas:
                tarefa = Tarefa.objects.get(pk=tar.pk)
                tarefa.status = 'PAUSA'
                tarefa.ultimo_tempo = timezone.now()
                tarefa.save()
                tarefa_evento = TarefaEvento()
                tarefa_evento.tarefa = tarefa
                tarefa_evento.evento = evento
                tarefa_evento.save()

        logout(request)
        return HttpResponseRedirect(reverse('home'))

    return render(request, 'accounts/encerramento.html', {})


@login_required(login_url='login')
def clienteSerie(request, pk):
    context = {}
    form = SerieForm(request.POST or None)
    cliente = Cliente.objects.get(pk=pk)
    vencimento = cliente.serie_dt
    if request.POST:
        serie = request.session.get('serie')
        if form.is_valid():
            vencimento = form.cleaned_data['vencimento']
            if request.POST.get('btn_limpar'):
                serie = None
                request.session['serie'] = serie
            elif request.POST.get('btn_gerar'):
                serie = gerarNumeroSerie(cliente, vencimento)
                request.session['serie'] = serie
                pass
            elif request.POST.get('btn_email'):
                # cliente.serie = serie
                # cliente.serie_dt = vencimento
                # cliente.save()
                messages.info(request, serie)
                pass
                # return HttpResponseRedirect(reverse('url_cliente_update', kwargs={'pk': cliente.pk}))
    else:
        serie = None

    context['form'] = form
    context['serie'] = serie
    context['cliente'] = cliente
    context['vencimento'] = vencimento
    return render(request, 'core/cliente_serie.html', context)


# @login_required
# def edit_password(request):
#     template_name = 'accounts/edit_password.html'
#     context = {}
#     if request.method == 'POST':
#         form = PasswordChangeForm(data=request.POST, user=request.user)
#         if form.is_valid():
#             form.save()
#             context['success'] = True
#     else:
#         form = PasswordChangeForm(user=request.user)
#     context['form'] = form
#     return render(request, template_name, context)


@login_required
def edit_password(request):
    template_name = 'accounts/edit_password.html'
    context = {}
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'alterado com sucesso')
            return HttpResponseRedirect(reverse('home'))
    else:
        form = PasswordChangeForm(user=request.user)
    context['form'] = form
    return render(request, template_name, context)


@login_required(login_url='login')
def userList(request):
    context = {}
    template_name = 'accounts/user_list.html'
    lista = User.objects.filter(is_consulta=False).order_by('name')

    page = request.GET.get('page', 1)
    paginator = Paginator(lista, 10)
    try:
        lista: paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages)

    context['lista'] = lista
    return render(request, template_name, context)
