import json
import os
import urllib
from datetime import datetime, date
from datetime import timedelta
import compliance.settings as conf

import boto3
import requests
from boto.s3.connection import S3Connection
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, Page
from django.db.models import Q, Max, Min, Count
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from validate_docbr import CNPJ
from werkzeug.utils import secure_filename

from compliance import settings
from compliance.accounts.models import User
from compliance.accounts.senha import gerar_senha_letras_numeros
from compliance.aws.form import UploadFileOnlyForm
from compliance.aws.views import get_s3_filename_list, get_nome, s3_upload_small_files, s3_delete_file
from compliance.core.form import ClienteForm, TarefaForm, MonitorForm, TarefaReopenForm, DocumentForm, \
    ClienteConsultaForm, ClienteAddUser, RelatorioForm
from compliance.core.mail import send_mail_template
from compliance.core.models import Cliente, Tarefa, Evento, TarefaEvento, MODULO_CHOICE, Documento, UserCliente, Backup, \
    CLIENTE_NIVELS


# api_url_base = 'http://3.224.26.231:8081/'
# userAndPass = b64encode(b"assist:123456").decode("ascii")
# headers = {'Content-Type': 'application/json',
#            'Authorization': 'Basic %s' % userAndPass}

def handler404(request):
    return render(request, 'error.html', status=404)


def TempoDecorrido(inicio, termino):
    # diferenca de tempo em segundos
    total = ((termino.toordinal() - inicio.toordinal()) * 24 * 60 * 60) + \
            ((termino.hour - inicio.hour) * 60 * 60) + \
            ((termino.minute - inicio.minute) * 60) + \
            (termino.second - inicio.second)
    return total


def addEventoTarefaMsg(request, tarefa, msg):
    evento = Evento()
    evento.descricao = msg
    evento.user = request.user
    if tarefa.cliente:
        evento.cliente = tarefa.cliente
    evento.save()

    tarefa_evento = TarefaEvento()
    tarefa_evento.tarefa = tarefa
    tarefa_evento.evento = evento
    tarefa_evento.save()


def addEventoTarefa(tarefa, evento):
    tarefa_evento = TarefaEvento()
    tarefa_evento.tarefa = tarefa
    tarefa_evento.evento = evento
    tarefa_evento.save()


@login_required(login_url='login')
def ClienteEventoList(request, pk):
    context = {}
    template_name = 'core/cliente_evento_list.html'
    cliente = Cliente.objects.get(pk=pk)
    eventos = Evento.objects.filter(cliente=cliente).order_by('created_at').reverse()

    page = request.GET.get('page', 1)
    paginator = Paginator(eventos, 10)
    try:
        lista: Page = paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages)

    context['lista'] = lista
    context['cliente'] = cliente
    return render(request, template_name, context)


def home_view(request):
    lista = []
    context = {}
    form = MonitorForm(request.GET or None)
    context['form'] = form
    tipo = request.GET.get('tipo', '1')

    if not tipo:
        tipo = '1'

    if tipo == '1':
        # lista = Cliente.objects.filter(Q(monitora=True)).order_by('nome')
        lista = Cliente.objects.order_by('nome')
    else:
        inicio = date.today()
        lista = Evento.objects \
            .values('cliente', 'cliente__nome') \
            .filter(setor__isnull=False, created_at__range=(inicio, inicio + timedelta(days=1))) \
            .annotate(prim_acesso=Min('created_at')) \
            .annotate(ult_acesso=Max('created_at')) \
            .annotate(qt_setor=Count('setor', distinct=True)) \
            .order_by('cliente__nome')

    context['lista'] = lista

    return render(request, "home.html", context)


@login_required(login_url='login')
def MonitorBackupNew(request):
    context = {}
    user_list = Cliente.objects.filter(Q(monitora=True)).order_by('nome')
    page = request.GET.get('page', 1)
    tipo = request.GET.get('tipo', 'BACKUP')

    paginator = Paginator(user_list, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    context['tipo'] = tipo
    context['lista'] = users
    return render(request, 'monitor.html', context)


@login_required(login_url='login')
def TarefaReopen(request, pk):
    context = {}
    tarefa = Tarefa.objects.get(pk=pk)
    cliente = Cliente.objects.get(pk=tarefa.cliente.pk)
    form = TarefaReopenForm(request.POST or None)

    if request.POST:
        try:
            tarefa.ultimo_tempo = timezone.now()
            tarefa.prioridade = request.POST.get('prioridade')
            tarefa.status = 'PAUSA'
            tarefa.encerrado_dt = None
            tarefa.implantado_dt = None
            tarefa.save()

            addEventoTarefaMsg(request, tarefa, 'reabertura/' + request.POST.get('motivo'))
            messages.success(request, 'reabertura de tarefa ' + str(tarefa.identificador) + ' realizada com sucesso')

        except Exception as e:
            messages.error(request, e)
            pass

        return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

    context['identificador'] = tarefa.identificador
    context['prioridade'] = tarefa.prioridadeToStr
    context['resumo'] = tarefa.resumo
    context['form'] = form
    context['cliente'] = cliente
    context['usuario'] = tarefa.user
    return render(request, 'core/cliente_tarefa_reopen.html', context)


@login_required(login_url='login')
def PausarTarefasMenos(request, tarefa_origem, msg):
    lst = Tarefa.objects.filter(user=request.user, \
                                iniciado_dt__isnull=False, encerrado_dt__isnull=True) \
        .exclude(status='PAUSA')

    if lst:
        evento = Evento()
        evento.descricao = msg
        evento.user = request.user
        evento.cliente = tarefa_origem.cliente
        evento.save()
        for tar in lst:
            if tar.pk != tarefa_origem.pk:
                tarefa = Tarefa.objects.get(pk=tar.pk)
                tarefa.status = 'PAUSA'
                tarefa.ultimo_tempo = timezone.now()
                tarefa.save()
                addEventoTarefa(tarefa, evento)


@login_required(login_url='login')
def ClienteTarefaList(request, pk):
    context = {}
    template_name = 'core/cliente_tarefa_list.html'
    cliente = Cliente.objects.get(pk=pk)
    lista = Tarefa.objects.filter(cliente=cliente, encerrado_dt__isnull=True) \
        .exclude(modulo='SAC').order_by('identificador').reverse()

    paginator = Paginator(lista, 10)
    try:
        page = request.GET.get('page') or '1'
        tarefas = paginator.page(page)
    except PageNotAnInteger:
        tarefas = paginator.page(1)
    except EmptyPage:
        tarefas = paginator.page(paginator.num_pages)

    context['lista'] = tarefas
    context['cliente'] = cliente
    context['page'] = page
    return render(request, template_name, context)


@login_required(login_url='login')
def clienteNew(request):
    cnpj = CNPJ()
    data = {}
    cliente = Cliente()
    form = ClienteForm(request.POST or None, instance=cliente)

    if form.is_valid():
        try:
            if not cnpj.validate(cliente.cnpj):
                raise Exception('cnpj inválido')

            cliente = form.save()
            return HttpResponseRedirect(reverse('url_cliente_update', kwargs={'pk': cliente.pk}))

        except Exception as e:
            messages.error(request, e)
            pass

    data['form'] = form
    data['cliente'] = cliente
    return render(request, 'core/cliente_edit.html', data)


@login_required(login_url='login')
def download(request, pk):
    documento = Documento.objects.get(pk=pk)
    absolute_path = '{}/{}'.format(settings.MEDIA_ROOT, str(documento.arquivo))
    response = FileResponse(open(absolute_path, 'rb'), as_attachment=True)
    return response


def get_lista_modulos():
    modulo_lista = [{"value": "TODOS", "label": "Todos"}, ]
    for m in MODULO_CHOICE:
        modulo_lista.append({"value": m[0], "label": m[1]})
    return modulo_lista


def get_lista_usuarios():
    lst = User.objects.filter(is_consulta=False).order_by('name')
    user_list = [{"value": "0", "label": "Todos"}, ]
    for u in lst:
        user_list.append({"value": str(u.pk), "label": u.name})
    return user_list


@login_required(login_url='login')
def TarefaLista(request):
    context = {}
    valor = ''
    usuario = str(request.user.pk)
    page = '1'
    filtro_modulo = Q()
    filtro_usuario = Q()
    filtro_cliente = Q()
    modulo = 'TODOS'

    user_list = get_lista_usuarios()
    modulo_lista = get_lista_modulos()

    if request.POST:
        valor = request.POST.get('pesquisa') or ''
        modulo = request.POST.get('modulo')
        usuario = request.POST.get('txt_usuario')

        for m in modulo_lista:
            if m.get('label') == modulo:
                modulo = m.get('value')

        for u in user_list:
            if u.get('value') == usuario:
                usuario = u.get('value')

        request.session['valor'] = valor
        request.session['modulo'] = modulo
        request.session['usuario'] = usuario

    elif request.GET:
        page = request.GET.get('page') or '1'
        valor = request.session.get('valor')
        modulo = request.session.get('modulo')
        usuario = request.session.get('usuario')

    if valor.isdigit():
        filtro_pesquisa = Q(Q(identificador=valor) | Q(cliente__cnpj=valor))
        filtro_status = Q()
    else:
        filtro_pesquisa = Q(Q(resumo__icontains=valor) | Q(cliente__nome__icontains=valor))
        filtro_status = Q(encerrado_dt__isnull=True)
        if modulo != 'TODOS':
            filtro_modulo = Q(modulo=modulo)
        if usuario != '0':
            filtro_usuario = Q(user=usuario)

    if request.user.is_consulta:
        clientes = []
        lst = UserCliente.objects.filter(user=request.user)
        for c in lst:
            clientes.append(c.cliente.pk)
        filtro_cliente = Q(cliente__in=clientes)

    lista = Tarefa.objects.filter(filtro_pesquisa, filtro_status, filtro_modulo, filtro_usuario,
                                  filtro_cliente).exclude(modulo='SAC').order_by('identificador').reverse()
    paginator = Paginator(lista, 10)
    try:
        tarefas = paginator.page(page)
    except PageNotAnInteger:
        tarefas = paginator.page(1)
    except EmptyPage:
        tarefas = paginator.page(paginator.num_pages)

    context['user_list'] = user_list
    context['modulo_lista'] = modulo_lista
    context['modulo'] = modulo
    context['txt_usuario'] = usuario
    context['pesquisa'] = valor
    context['lista'] = tarefas

    return render(request, 'core/tarefa_list.html', context)


@login_required(login_url='login')
def ClienteBackup(request, pk, arquivo):
    cliente = Cliente.objects.get(pk=pk)
    try:
        backup = Backup.objects.get(arquivo__iexact=arquivo, cliente=cliente.pk)
        url = urllib.parse.quote_plus('/clientes/cli-' + cliente.cnpj + '/' + backup.arquivo)
    except:
        backup = None
        url = None
    context = {
        'cliente': cliente,
        'backup': backup if backup else None,
        'arquivo': arquivo,
        'url': url
    }
    return render(request, 'core/cliente_backup.html', context)


def AddClienteUser(cliente, nome, email):
    template_mail = 'accounts/email_password.html'
    # prepara senha
    senha = gerar_senha_letras_numeros(6)
    hasher = PBKDF2PasswordHasher()
    salt = hasher.salt()
    # cria usuario
    try:
        usuario = User()
        usuario.name = cliente.nome
        usuario.username = nome
        usuario.celular = cliente.celular
        usuario.email = email
        usuario.is_consulta = True
        usuario.password = hasher.encode(senha, salt)
        usuario.save()
    except:
        raise Exception('verifique se e-mail ou nome de usuário já existe')

    # relaciona usuario com cliente
    uc = UserCliente()
    uc.user = usuario
    uc.cliente = cliente
    uc.save()

    context_mail = {
        'username': usuario.username,
        'keyuser': senha,
        'email': usuario.email,
        'mensagem': 'Sr(a): ' + usuario.name +
                    '\n Segue senha de acesso'
                    '\n Link: assistcompliance.com.br (colocar o correto)'
                    '\n Para sua segurança, acesse o sistema e modifique sua senha',
    }
    send_mail_template(
        'senha de acesso',
        template_mail,
        context_mail,
        [usuario.email]
    )


@login_required(login_url='login')
def ClienteUsuario(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    form = ClienteAddUser(request.GET or None)
    if request.POST:
        try:
            nome = request.POST.get('nome')
            email = request.POST.get('email')
            AddClienteUser(cliente, nome, email)
            messages.success(request, 'cadastro realizado com sucesso')
            return HttpResponseRedirect(reverse('url_cliente_update', kwargs={'pk': cliente.pk}))
        except Exception as e:
            messages.error(request, e)
            pass

    context = {
        'cliente': cliente,
        'form': form
    }
    return render(request, 'core/cliente_usuario.html', context)


@login_required(login_url='login')
def ClienteFolderAWS(request, pk, folder):
    folder = urllib.parse.unquote(folder)
    cliente = Cliente.objects.get(pk=pk)
    if request.method == 'POST':
        form = UploadFileOnlyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file_name = folder + secure_filename(request.FILES['file'].name)
                s3_upload_small_files(request.FILES['file'],
                                      settings.AWS_STORAGE_BUCKET_NAME,
                                      file_name,
                                      request.content_type)
                # messages.info(request, 'arquivo enviado com sucesso')
            except Exception as e:
                messages.error(request, e)
    else:
        form = UploadFileOnlyForm()
    lista = get_s3_filename_list(folder)
    context = {
        'form': form,
        'folder': folder,
        'cliente': cliente,
        'lista': lista,
        'usuario': request.user
    }
    return render(request, 'core/cliente_aws.html', context)


def downloadObjectS3(request, nome):
    arquivo = urllib.parse.unquote(nome)
    file_path = '/tmp/' + get_nome(arquivo)  # file
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, arquivo, file_path)
    try:
        with open(file_path, 'rb') as fh:
            if '.pdf' in file_path:
                response = HttpResponse(fh.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            else:
                response = HttpResponse(fh.read(), content_type='application/force-download')
                response['Content-Disposition: attachment'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    except Exception as e:
        messages.error(request, e)
    # pass
    # raise Http404


@login_required(login_url='login')
def clienteUpdate(request, pk):
    context = {}
    cliente = Cliente.objects.get(pk=pk)
    usuarios = UserCliente.objects.filter(cliente=cliente)

    if request.user.is_consulta:
        form = ClienteConsultaForm(request.POST or None, instance=cliente)
    else:
        form = ClienteForm(request.POST or None, instance=cliente)

    if request.method == 'POST':
        if request.POST.get('btn_ativa'):
            cliente.is_active = not cliente.is_active
            cliente.save()
            return HttpResponseRedirect(reverse('url_cliente_update', kwargs={'pk': cliente.pk}))
        if request.POST.get('btn_add_user'):
            if AddClienteUser(request, cliente):
                messages.success(request, 'Usuário adicionado com sucesso')
            return HttpResponseRedirect(reverse('url_cliente_update', kwargs={'pk': cliente.pk}))
        if form.is_valid():
            cliente = Cliente.objects.get(pk=pk)
            cliente.nome = form.data.get('nome')
            cliente.monitora = form.data.get('monitora') or cliente.monitora
            cliente.nivel = form.data.get('nivel')
            cliente.fone = form.data.get('fone')
            cliente.celular = form.data.get('celular')
            cliente.email = form.data.get('email')
            cliente.logradouro = form.data.get('logradouro')
            cliente.bairro = form.data.get('bairro')
            cliente.numero = form.data.get('numero')
            cliente.contato = form.data.get('contato')
            cliente.cidade = form.data.get('cidade')
            cliente.pode_sms = form.data.get('pode_sms')
            cliente.pode_lgpd = form.data.get('pode_lgpd')
            cliente.uf = form.data.get('uf')
            cliente.cep = form.data.get('cep')
            cliente.complemento = form.data.get('complemento')
            cliente.save()
            messages.success(request, 'modificado com sucesso')

    context['form'] = form
    context['cliente'] = cliente
    context['sem_usuario'] = not usuarios

    return render(request, 'core/cliente_edit.html', context)


@login_required(login_url='login')
def ClienteTarefaNew(request, pk):
    context = {}
    cliente = Cliente.objects.get(pk=pk)
    tarefa = Tarefa()
    tarefa.user = request.user
    form = TarefaForm(request.POST or None, instance=tarefa)
    if request.method == 'POST':
        try:
            if not tarefa.user:
                tarefa.user = request.user
            tarefa.cliente = cliente
            tarefa.solicitante = request.POST.get('solicitante')
            tarefa.celular = request.POST.get('celular')
            tarefa.email = request.POST.get('email')
            tarefa.modulo = request.POST.get('modulo')
            tarefa.resumo = request.POST.get('resumo')
            tarefa.demanda = request.POST.get('demanda')
            if not tarefa.identificador:
                ultimo = Tarefa.objects.aggregate(Max('identificador'))['identificador__max'] or 0
                ultimo += 1
                tarefa.identificador = ultimo

            tarefa.save()
            addEventoTarefaMsg(request, tarefa, 'inclusão de tarefa / ' + str(tarefa.identificador))
            messages.success(request, 'gravado com sucesso')
            return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

        except Exception as e:
            messages.error(request, e)
            pass

    context['form'] = form
    context['tarefa'] = tarefa
    context['cliente'] = cliente
    context['status'] = tarefa.getStatusSAC(request.user)

    return render(request, 'core/cliente_tarefa_edit.html', context)


@login_required(login_url='login')
def TarefaImprimir(request, pk):
    tarefa = Tarefa.objects.get(pk=pk)
    url = settings.COMPLIANCE_URL + 'tarefa/imprimir/'
    response = requests.post(url, tarefa.dump(), auth=("assist", "123456"))
    if response.status_code == 200:
        return FileResponse(open(response.text, 'rb'), content_type='application/pdf')
    else:
        return HttpResponse(response.status_code)


def home(request):
    context = {}
    template = loader.get_template('home.html')

    if request.user.is_authenticated:
        if request.user.pk:
            request.session['is_consulta'] = request.user.is_consulta

            if request.user.is_consulta:
                return HttpResponseRedirect(reverse('url_cliente_list'))

            filtro_status = Q(encerrado_dt__isnull=True, user=request.user)
            filtro_tipo = Q(Q(status='PRODUCAO') | Q(status='PAUSA'))
            lista = Tarefa.objects.filter(filtro_status, filtro_tipo).order_by('identificador').reverse()
            context['lista'] = lista
        else:
            request.session['is_consulta'] = None
    else:
        return HttpResponseRedirect(reverse('login'))

    return HttpResponse(template.render(context, request))


@login_required(login_url='login')
def ClienteTarefaEdit(request, pk):
    msgevento = ''
    context = {}
    tarefa = Tarefa.objects.get(pk=pk)
    cliente = Cliente.objects.get(pk=tarefa.cliente.pk)
    usuarios = User.objects.filter(Q(is_des=not request.user.is_des), Q(is_consulta=False)).exclude(pk=request.user.pk)

    form = TarefaForm(request.POST or None, instance=tarefa)
    form_upload = UploadFileOnlyForm(request.POST, request.FILES)

    if (request.POST.get('btn_imprimir') or request.POST.get('btn_imprimir')) and tarefa.pk:
        TarefaImprimir(request, tarefa.pk)

    if request.method == 'POST':
        try:

            if request.POST.get('btn_update_incliente'):
                tarefa.implantado_dt = timezone.now()
                addEventoTarefaMsg(request, tarefa, 'atualização no cliente')
                tarefa.save()
                return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

            if request.POST.get('btn_observar') and request.POST.get('observacao'):
                valor = [tarefa.demanda, chr(13),
                         datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' / ' + request.user.name, chr(13),
                         request.POST.get('observacao')]
                tarefa.demanda = "".join(valor)
                tarefa.save()
                return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

            usuario = User.objects.get(pk=request.POST.get('user_encaminha'))
            msgevento = request.POST.get('msgevento')

            if tarefa.pk and tarefa.ultimo_tempo:
                tempo = TempoDecorrido(tarefa.ultimo_tempo.astimezone(), datetime.now())

            # inicia a produção da tarefa
            if (request.POST.get('btn_start') or request.POST.get('btn_reinicia')) and tarefa.pk:
                # calcula tempo ocioso
                if tarefa.status == 'PAUSA':
                    msg = 'reinício em produção'
                    if tarefa.tempo_ocioso:
                        tarefa.tempo_ocioso = tarefa.tempo_ocioso + tempo
                    else:
                        tarefa.tempo_ocioso = tempo
                if not tarefa.iniciado_dt:
                    msg = 'início em produção'
                    tarefa.iniciado_dt = timezone.now()

                tarefa.modulo = request.POST.get('modulo')
                tarefa.user = request.user
                tarefa.ultimo_tempo = timezone.now()
                tarefa.status = 'PRODUCAO'
                tarefa.save()
                messages.success(request, 'sucesso no ' + msg)
                addEventoTarefaMsg(request, tarefa, msg)

                if tarefa.identificador:
                    msg = msg + ' de ' + str(tarefa.identificador)
                PausarTarefasMenos(request, tarefa, 'pausa/' + msg)

                return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

            # pausar a tarefa
            if request.POST.get('btn_pausa') and tarefa.status == 'PRODUCAO':
                if tarefa.tempo_produtivo:
                    tarefa.tempo_produtivo = tarefa.tempo_produtivo + tempo
                else:
                    tarefa.tempo_produtivo = tempo
                tarefa.status = 'PAUSA'
                tarefa.ultimo_tempo = timezone.now()
                tarefa.save()
                messages.success(request, 'pausa realizada com sucesso')
                addEventoTarefaMsg(request, tarefa, ('pausa/' + msgevento) if msgevento else 'pausa')
                return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

            # encerrar a tarefa
            if (request.POST.get('btn_encerra') or request.POST.get('btn_cancela')) and tarefa.pk:
                msg = ''
                if tarefa.status == 'PRODUCAO':
                    if tarefa.tempo_produtivo:
                        tarefa.tempo_produtivo = tarefa.tempo_produtivo + tempo
                    else:
                        tarefa.tempo_produtivo = tempo
                elif tarefa.status == 'PAUSA':
                    if tarefa.tempo_ocioso:
                        tarefa.tempo_ocioso = tarefa.tempo_ocioso + tempo
                    else:
                        tarefa.tempo_ocioso = tempo
                elif tarefa.status == 'ANALISE':
                    if tarefa.tempo_analise:
                        tarefa.tempo_analise = tarefa.tempo_analise + tempo
                    else:
                        tarefa.tempo_analise = tempo

                if request.POST.get('btn_encerra'):
                    tarefa.status = 'ENCERRADO'
                    msg = 'encerramento de tarefa'

                if request.POST.get('btn_cancela'):
                    tarefa.status = 'CANCELADO'
                    msg = 'cancelamento de tarefa'

                if msgevento:
                    msg = msg + '/' + msgevento

                tarefa.encerrado_dt = timezone.now()
                tarefa.save()
                messages.success(request, 'sucesso no ' + msg)
                addEventoTarefaMsg(request, tarefa, msg)
                return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

            # liberar para análise
            if request.POST.get('btn_analise'):
                if tarefa.status == 'PRODUCAO':
                    if tarefa.tempo_produtivo:
                        tarefa.tempo_produtivo = tarefa.tempo_produtivo + tempo
                    else:
                        tarefa.tempo_produtivo = tempo
                if tarefa.status == 'PAUSA':
                    if tarefa.tempo_ocioso:
                        tarefa.tempo_ocioso = tarefa.tempo_ocioso + tempo
                    else:
                        tarefa.tempo_ocioso = tempo
                if tarefa.status == 'ANALISE':
                    tarefa.status = 'PAUSA'
                    if not msgevento:
                        msgevento = 'tarefa liberada para desenvolvimento'
                else:
                    tarefa.status = 'ANALISE'
                    if not msgevento:
                        msgevento = 'tarefa liberada para análise'

                tarefa.ultimo_tempo = timezone.now()
                if usuario:
                    tarefa.user = usuario
                    tarefa.status = 'PAUSA'

                tarefa.save()
                messages.success(request, 'realizado com sucesso')
                addEventoTarefaMsg(request, tarefa, msgevento)

                return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

            if form.is_valid():
                tarefa.solicitante = request.POST.get('solicitante')
                tarefa.celular = request.POST.get('celular')
                tarefa.email = request.POST.get('email')
                tarefa.modulo = request.POST.get('modulo')
                tarefa.resumo = request.POST.get('resumo')
                tarefa.demanda = request.POST.get('demanda')
                if not tarefa.user:
                    tarefa.user = request.user

                tarefa.save()
                messages.success(request, 'tarefa gravada com sucesso')
                return HttpResponseRedirect(reverse('url_cliente_tarefa_edit', kwargs={'pk': tarefa.pk}))

        except Exception as e:
            messages.error(request, e)

    else:
        context['is_valid'] = False

    lista_eventos = TarefaEvento.objects.filter(Q(tarefa=tarefa)).order_by('pk').reverse()
    bloqueado = (tarefa.user and (
            tarefa.encerrado_dt or not cliente.is_active or request.user != tarefa.user)) \
                or request.user.is_consulta or tarefa.status != 'INICIO'

    context['form'] = form
    context['demanda'] = tarefa.demanda
    context['bloqueado'] = bloqueado
    context['tarefa'] = tarefa
    context['cliente'] = cliente
    context['msgevento'] = msgevento
    context['eventos'] = lista_eventos
    context['usuarios'] = usuarios
    context['usuario'] = tarefa.user
    context['status'] = tarefa.getStatusSAC(request.user)
    context['form_upload'] = form_upload

    return render(request, 'core/cliente_tarefa_edit.html', context)


@login_required(login_url='login')
def ClienteAWS(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    folder = "clientes/cli-" + cliente.cnpj + '/'
    if request.method == 'POST':
        form = UploadFileOnlyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file_name = folder + secure_filename(request.FILES['file'].name)
                s3_upload_small_files(request.FILES['file'],
                                      settings.AWS_STORAGE_BUCKET_NAME,
                                      file_name,
                                      request.content_type)
                messages.info(request, 'arquivo enviado com sucesso')
            except Exception as e:
                messages.error(request, e)
    else:
        form = UploadFileOnlyForm()
    lista = get_s3_filename_list(folder)
    context = {
        'form': form,
        'folder': folder,
        'cliente': cliente,
        'lista': lista,
        'usuario': request.user
    }
    return render(request, 'core/cliente_aws.html', context)


@login_required(login_url='login')
def TarefaAnexo(request, pk):
    context = {}
    tarefa = Tarefa.objects.get(pk=pk)
    cliente = Cliente.objects.get(pk=tarefa.cliente.pk)
    folder = "tarefas/" + str(tarefa.pk) + '/'
    if request.method == 'POST':
        form = UploadFileOnlyForm(request.POST, request.FILES)
        if form.is_valid():
            file_name = folder + secure_filename(request.FILES['file'].name)
            s3_upload_small_files(request.FILES['file'],
                                  settings.AWS_STORAGE_BUCKET_NAME,
                                  file_name,
                                  request.content_type)
            return HttpResponseRedirect(reverse('url_tarefa_anexo', kwargs={'pk': tarefa.pk}))
    else:
        form = UploadFileOnlyForm()
    lista = get_s3_filename_list(folder)
    context['lista'] = lista
    context['form'] = form
    context['tarefa'] = tarefa
    context['cliente'] = cliente
    context['usuario'] = tarefa.user
    return render(request, 'core/cliente_tarefa_anexo.html', context)


def TarefaRemoveAnexo(request, pk, nome):
    try:
        arquivo = urllib.parse.unquote(nome)
        response = s3_delete_file(settings.AWS_STORAGE_BUCKET_NAME, arquivo)
        # messages.success(request, response.HTTPStatusCode)
        return HttpResponseRedirect(reverse('url_tarefa_anexo', kwargs={'pk': pk}))
    except Exception as e:
        messages.error(request, e)


@login_required(login_url='login')
def ClienteListView(request):
    context = {}
    valor = ""
    page = "1"
    nivel = 'TODOS'
    filtro_nivel = Q()
    nivel_lista = [{"value": "TODOS", "label": "Todos"}, ]
    for m in CLIENTE_NIVELS:
        nivel_lista.append({"value": m[0], "label": m[1]})
    if request.POST:
        valor = request.POST.get('pesquisa') or ''
        request.session['valor'] = valor
        nivel = request.POST.get('nivel')
        request.session['nivel'] = nivel
    elif request.GET:
        page = request.GET.get('page') or '1'
        valor = request.session.get('valor') or ''
        nivel = request.session.get('nivel')

    if request.user.is_consulta:
        clientes = []
        lst = UserCliente.objects.filter(user=request.user)
        for c in lst:
            clientes.append(c.cliente.pk)
        if len(clientes) == 1:
            return HttpResponseRedirect(reverse('url_cliente_update', kwargs={'pk': clientes[0]}))
        else:
            lista = Cliente.objects.filter(pk__in=clientes)
    else:
        if nivel != 'TODOS':
            filtro_nivel = Q(nivel=nivel, is_active=True)
        lista = Cliente.objects \
            .filter(Q(Q(nome__icontains=valor) | Q(cnpj__icontains=valor)), filtro_nivel) \
            .order_by('nome')

    paginator = Paginator(lista, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    context['lista'] = users
    context['page'] = page
    context['pesquisa'] = valor
    context['nivel_lista'] = nivel_lista
    context['nivel'] = nivel

    return render(request, 'core/cliente_list.html', context)


def getListaTarefa(request):
    filtro_cliente = Q()
    filtro_periodo = Q()
    filtro_usuario = Q()
    filtro_modulo = Q()
    situacao = request.POST.get('situacao')
    data_inicial = request.POST.get('data_inicial')
    data_final = request.POST.get('data_final')

    valor = request.POST.get('nome') or ''
    if valor.isdigit():
        filtro_nome = Q(Q(identificador=valor) | Q(cliente__cnpj=valor))
    else:
        filtro_nome = Q(Q(resumo__icontains=valor) | Q(cliente__nome__icontains=valor))

    if situacao == '0':  # todos
        filtro_periodo = Q(created_at__range=[data_inicial, data_final])
    elif situacao == '1':  # não iniciado
        filtro_periodo = Q(created_at__range=[data_inicial, data_final], encerrado_dt__isnull=True,
                           iniciado_dt__isnull=True)
    elif situacao == '2':  # em produção
        filtro_periodo = Q(created_at__range=[data_inicial, data_final], encerrado_dt__isnull=True,
                           iniciado_dt__isnull=False)
    elif situacao == '3':  # atualizado no cliente
        filtro_periodo = Q(implantado_dt__range=[data_inicial, data_final])
    elif situacao == '4':  # encerrada
        filtro_periodo = Q(encerrado_dt__range=[data_inicial, data_final])

    if request.POST.get('modulo') != 'TODOS':
        filtro_modulo = Q(modulo=request.POST.get('modulo'))

    if request.user.is_consulta:
        clientes = []
        lst = UserCliente.objects.filter(user=request.user)
        for c in lst:
            clientes.append(c.cliente.pk)
        filtro_cliente = Q(cliente__in=clientes)
    elif not (request.POST.get('usuario') == '0'):
        filtro_usuario = Q(user=request.POST.get('usuario'))

    lista = []
    tarefas = Tarefa.objects.filter(filtro_periodo, filtro_usuario, filtro_modulo, filtro_nome, filtro_cliente) \
        .exclude(modulo='SAC') \
        .order_by('identificador')
    for tar in tarefas:
        if situacao == '0' or situacao == '1':
            data = tar.created_at
        elif situacao == '2':
            data = tar.iniciado_dt
        elif situacao == '3':
            data = tar.implantado_dt
        elif situacao == '4':
            data = tar.encerrado_dt
        lista.append({
            "identificador": tar.identificador,
            "resumo": tar.resumo,
            "modulo": tar.modulo,
            "data": data.strftime('%d/%m/%Y') if data else '',
            "nome": tar.cliente.nome
        })

    return lista


def getTituloRelatorio(request):
    titulo = ''
    if request.POST.get('situacao') == "0":
        titulo += ' Não iniciado'
    elif request.POST.get('situacao') == "1":
        titulo += ' Em produção'
    elif request.POST.get('situacao') == "2":
        titulo += ' Atualizado no cliente'
    elif request.POST.get('situacao') == "3":
        titulo += ' Encerrada'
    titulo += ' Período '
    data = datetime.strptime(request.POST.get('data_inicial'), '%Y-%m-%d')
    titulo += ' de ' + data.strftime('%d/%m/%Y')
    data = datetime.strptime(request.POST.get('data_final'), '%Y-%m-%d')
    titulo += ' a ' + data.strftime('%d/%m/%Y')
    return titulo


@login_required(login_url='login')
def GeradorRelatorio(request):
    lista = []
    context = {}
    situacao = request.POST.get('situacao') or '2'
    data = datetime.today().strftime('%Y-%m-%d')
    data_inicial = request.POST.get('data_inicial') or data
    data_final = request.POST.get('data_final') or data
    usuario = request.POST.get('usuario') or ''
    modulo = request.POST.get('modulo') or ''
    nome = request.POST.get('nome') or ''
    if request.POST:
        lista = getListaTarefa(request)
        if request.POST.get('btn_imprimir'):
            url = settings.COMPLIANCE_URL + 'lista_tarefa/'
            data = {
                "titulo": getTituloRelatorio(request),
                "lista": lista
            }
            response = requests.post(url, json.dumps(data), auth=("assist", "123456"))
            if response.status_code == 200:
                return FileResponse(open(response.text, 'rb'), content_type='application/pdf')
            else:
                return HttpResponse(response.status_code)
    context['situacao'] = situacao
    context['usuario'] = usuario
    context['modulo'] = modulo
    context['nome'] = nome
    context['user_list'] = get_lista_usuarios()
    context['modulo_lista'] = get_lista_modulos()
    context['data_inicial'] = data_inicial
    context['data_final'] = data_final
    context['lista'] = lista

    return render(request, 'core/relatorio.html', context)


@login_required(login_url='login')
def acessos(request):
    lista = []
    context = {}
    data = datetime.today().strftime('%Y-%m-%d')
    data_inicial = request.POST.get('data_inicial') or data

    inicio = datetime.strptime(data_inicial, "%Y-%m-%d")
    termino = inicio.date() + timedelta(days=1)

    lista = Evento.objects \
        .values('cliente', 'cliente__nome') \
        .filter(setor__isnull=False, created_at__range=(inicio.isoformat(), termino.isoformat())) \
        .annotate(prim_acesso=Min('created_at')) \
        .annotate(ult_acesso=Max('created_at')) \
        .annotate(qt_setor=Count('setor', distinct=True)) \
        .order_by('cliente__nome')

    context['lista'] = lista
    context['data_inicial'] = data_inicial

    return render(request, "acessos.html", context)
