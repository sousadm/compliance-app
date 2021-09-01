# Create your views here.
import hashlib
import json

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone, dateformat, formats
from validate_docbr import CPF
from werkzeug.utils import secure_filename

from compliance import settings
from compliance.aws.form import UploadFileOnlyForm
from compliance.aws.views import s3_upload_small_files
from compliance.core.mail import send_mail_template
from compliance.core.models import Cliente, Evento, Documento
from compliance.core.report import render_to_pdf
from compliance.lgpd.models import Consentimento, ConsentimentoEvento, Tratamento, TratamentoEvento

lista_1 = [
    {"id": "I", "descricao": "I – confirmação da existência de tratamento"}
]
lista_2 = [
    {"id": "II", "descricao": "II – acesso aos dados"},
    {"id": "III", "descricao": "III - correção de dados incompletos, inexatos ou desatualizados"},
    {"id": "IV", "descricao": "IV - anonimidade, bloqueio ou eliminação de dados desnecessários"},
    {"id": "V", "descricao": "V - portabilidade dos dados a outro fornecedor de serviço ou produto"},
    {"id": "VI", "descricao": "VI – eliminação dos dados pessoais tratados"},
    {"id": "VII", "descricao": "VII – informação sobre compartilhado de dados"},
    {"id": "VIII", "descricao": "VIII – informação sobre consentimento e consequências da negativa"},
    {"id": "IX", "descricao": "IX - revogação do consentimento"}
]


def get_data_impressao(request, cliente):
    lista_finalidade = []
    if request.POST.get('finalidade_1'):
        lista_finalidade.append(request.POST.get('finalidade_1'))
    if request.POST.get('finalidade_2'):
        lista_finalidade.append(request.POST.get('finalidade_2'))
    if request.POST.get('finalidade_3'):
        lista_finalidade.append(request.POST.get('finalidade_3'))
    lista_tratamento = []
    valor = request.session.get('consentimentos')
    for c in valor:
        if request.POST.get(c.get('tipo')):
            lista_tratamento.append(c.get('valor'))
    return {
        'datahora': dateformat.format(datetime.now(), formats.get_format('DATE_FORMAT')),
        'controlador_local': cliente.cidade,
        'controlador_nome': cliente.nome,
        'controlador_endereco': cliente.endereco_completo,
        'controlador_cnpj': cliente.cnpj,
        'nome': request.POST.get('nome'),
        'identidade': request.POST.get('identidade'),
        'cpf': request.POST.get('cpf'),
        'nacionalidade': request.POST.get('nacionalidade'),
        'estadocivil': request.POST.get('estadocivil'),
        'lista_tratamento': ", ".join(lista_tratamento),
        'lista_finalidade': ", ".join(lista_finalidade),
    }


def tratar_requisicao(obj, request, autorizador):
    cpf = CPF()
    if not cpf.validate(obj['cpf']):
        raise Exception('CPF inválido')
    prova = hashlib.md5(bytes(request.POST.get('autorizador'), 'utf-8')).hexdigest()
    if prova != autorizador:
        raise Exception('Código de autorização incorreto, verifique em seu e-mail e digite novamente')
    obj['nome'] = request.POST.get('nome')
    obj['cpf'] = request.POST.get('cpf')
    obj['email'] = request.POST.get('email')
    obj['telefone'] = request.POST.get('telefone')
    obj['celular'] = request.POST.get('celular')
    obj['whatsapp'] = request.POST.get('whatsapp')
    obj['banco'] = request.POST.get('banco')
    obj['agencia'] = request.POST.get('agencia')
    obj['conta'] = request.POST.get('conta')
    obj['ident_numero'] = request.POST.get('ident_numero')
    obj['ident_emissao'] = request.POST.get('ident_emissao')
    obj['nome_pai'] = request.POST.get('nome_pai')
    obj['nome_mae'] = request.POST.get('nome_mae')
    obj['titulo_numero'] = request.POST.get('titulo_numero')
    obj['reservista_numero'] = request.POST.get('reservista_numero')
    obj['cnh_numero'] = request.POST.get('cnh_numero')


def DefineConsentimentoEvento(cliente, consentimento, descricao):
    evento = Evento()
    evento.descricao = descricao
    evento.cliente = cliente
    evento.save()
    cons_evento = ConsentimentoEvento()
    cons_evento.evento = evento
    cons_evento.consentimento = consentimento
    cons_evento.save()


def get_tratamentos(request):
    tratamentos = []
    if request.POST.get('finalidade_1'):
        tratamentos.append(request.POST.get('finalidade_1'))
    if request.POST.get('finalidade_2'):
        tratamentos.append(request.POST.get('finalidade_2'))
    if request.POST.get('finalidade_3'):
        tratamentos.append(request.POST.get('finalidade_3'))
    return tratamentos


def tratar_dados_obj(request, obj):
    if request.POST.get('nome'):
        obj['nome'] = request.POST.get('nome')
    if request.POST.get('cpf'):
        obj['cpf'] = request.POST.get('cpf')
    if request.POST.get('email'):
        obj['email'] = request.POST.get('email')
    if request.POST.get('ende_numero'):
        obj['ende_numero'] = request.POST.get('ende_numero')
    if request.POST.get('ende_logra'):
        obj['ende_logra'] = request.POST.get('ende_logra')
    if request.POST.get('ende_uf'):
        obj['ende_uf'] = request.POST.get('ende_uf')
    if request.POST.get('ende_cep'):
        obj['ende_cep'] = request.POST.get('ende_cep')
    if request.POST.get('ende_bairro'):
        obj['ende_bairro'] = request.POST.get('ende_bairro')
    if request.POST.get('ende_cidade'):
        obj['ende_cidade'] = request.POST.get('ende_cidade')
    if request.POST.get('ende_compl'):
        obj['ende_compl'] = request.POST.get('ende_compl')
    if request.POST.get('celular'):
        obj['celular'] = request.POST.get('celular')
    if request.POST.get('telefone'):
        obj['telefone'] = request.POST.get('telefone')
    if request.POST.get('whatsapp'):
        obj['whatsapp'] = request.POST.get('whatsapp')
    if request.POST.get('banco'):
        obj['banco'] = request.POST.get('banco')
    if request.POST.get('agencia'):
        obj['agencia'] = request.POST.get('agencia')
    if request.POST.get('conta'):
        obj['conta'] = request.POST.get('conta')
    if request.POST.get('ident_numero'):
        obj['ident_numero'] = request.POST.get('ident_numero')
    if request.POST.get('ident_emissao'):
        obj['ident_emissao'] = request.POST.get('ident_emissao')
    if request.POST.get('nome_pai'):
        obj['nome_pai'] = request.POST.get('nome_pai')
    if request.POST.get('nome_mae'):
        obj['nome_mae'] = request.POST.get('nome_mae')
    if request.POST.get('titulo_numero'):
        obj['titulo_numero'] = request.POST.get('titulo_numero')
    if request.POST.get('reservista_numero'):
        obj['reservista_numero'] = request.POST.get('reservista_numero')
    if request.POST.get('cnh_numero'):
        obj['cnh_numero'] = request.POST.get('cnh_numero')


def LgpdConsentimento(request, pk):
    obj = {}
    context = {}
    try:
        consentimento = Consentimento.objects.get(pk=pk)
        empresa = Cliente.objects.get(pk=consentimento.cliente.pk)
        if not consentimento.autorizado_dt:
            url = settings.LGPD_URL + 'cnpj=' + str(consentimento.cliente.cnpj) + '/consentimento/' + str(pk)
            response = requests.get(url, auth=("assist", "123456"))
            obj = json.loads(response.text)
            tratar_dados_obj(request, obj)

        ident_emissao = datetime.today()
        autorizador = ""
        context = {
            'obj': obj,
            'autorizador': autorizador,
            'ident_emissao': ident_emissao.strftime('%Y-%m-%d'),
            'empresa': empresa
        }
        if request.method == 'POST':
            url = settings.LGPD_URL + 'criptografar/numero=' + str(consentimento.pk)
            tratar_requisicao(obj, request, consentimento.autorizador)
            response = requests.post(url, json.dumps(obj), auth=("assist", "123456"))
            if response.status_code == 200:
                consentimento = Consentimento.objects.get(pk=pk)
                consentimento.cpf = obj['cpf']
                consentimento.nome = obj['nome']
                consentimento.autorizado_dt = timezone.now()
                consentimento.save()
                DefineConsentimentoEvento(empresa, consentimento,
                                          'consentimento autorizado por ' + obj['nome'] + ' cpf:' + request.POST.get(
                                              'cpf'))
                return HttpResponseRedirect(reverse('lgpd_consulta', kwargs={'cpf': request.POST.get('cpf')}))
            else:
                messages.warning(request, response.text)
                pass

    except Exception as e:
        messages.error(request, e)

    return render(request, 'lgpd/consentimento.html', context)


def LgpdConsultaTitularCPF(request, cpf):
    try:
        lista = Consentimento.objects \
            .filter(cpf=cpf, autorizado_dt__isnull=False, revogacao_dt__isnull=True)
    except Exception as e:
        messages.error(request, e)
    context = {
        "cpf": cpf,
        "lista": lista
    }
    return render(request, 'lgpd/consulta.html', context)


def LgpdConsultaTitular(request):
    lista = []
    try:
        cpf = request.POST.get('cpf') or ''
        if request.POST and cpf:
            lista = Consentimento.objects \
                .filter(cpf=cpf, autorizado_dt__isnull=False, revogacao_dt__isnull=True)
    except Exception as e:
        messages.error(request, e)
    context = {
        "bloqueia": True,
        "cpf": cpf,
        "lista": lista
    }

    return render(request, 'lgpd/consulta.html', context)


@login_required(login_url='login')
def LgpdControladorTratamento(request, pk):
    context = {}
    try:
        cliente = Cliente.objects.get(pk=pk)
        lista = Tratamento.objects.filter(consentimento__cliente=cliente).order_by('id').reverse()

    except Exception as e:
        messages.error(request, e)

    context['cliente'] = cliente
    context['lista'] = lista

    return render(request, 'lgpd/controlador_tratamento.html', context)


@login_required(login_url='login')
def LgpdTratamentoDados(request, pk):
    obj = {}
    context = {}
    try:
        consentimento = Consentimento.objects.get(pk=pk)
        url = settings.LGPD_URL + 'cnpj=' + str(consentimento.cliente.cnpj) + '/consentimento/' + str(pk)
        response = requests.get(url, auth=("assist", "123456"))
        if response.status_code == 200:
            obj = json.loads(response.text)

        cliente = Cliente.objects.get(pk=pk)

    except Exception as e:
        messages.error(request, e)
    context['obj'] = obj
    context['consentimento'] = consentimento
    context['cliente'] = cliente

    return render(request, 'lgpd/tratamento_dados.html', context)


def LgpdTratamentoId(request, pk):
    context = {}
    lista = lista_2
    consentimento = Consentimento.objects.get(pk=pk)
    empresa = Cliente.objects.get(pk=consentimento.cliente.pk)
    selecionado = request.POST.get('opcao') or ''
    hashcode = ''
    titular = {
        'nome': request.POST.get('nome') or '',
        'cpf': request.POST.get('cpf') or ''
    }

    opcao = ''
    opcao_id = request.POST.get('opcao_id') or 'II'
    for n in lista:
        if selecionado == n['id']:
            opcao_id = n['id']
            opcao = n['descricao']
            break

    if request.method == 'POST':
        tratamento = Tratamento()
        tratamento.consentimento = consentimento
        tratamento.email = request.POST.get('email')
        tratamento.celular = request.POST.get('celular') or ''
        tratamento.protocolo = request.POST.get('protocolo')
        hashcode = request.POST.get('hashcode') or ''
        if request.POST.get('btn_solicitar'):
            url = settings.LGPD_URL + 'codigo_autorizacao'
            dados = {
                "email": request.POST.get('email'),
                "nome": request.POST.get('nome'),
                "assunto": "LGPD Código Autorização"
            }
            response = requests.post(url, json.dumps(dados), auth=("assist", "123456"))
            if response.status_code == 200:
                hashcode = response.text
            else:
                messages.error(request, response.text)

        if request.POST.get('btn_gravar'):
            prova = hashlib.md5(bytes(request.POST.get('protocolo'), 'utf-8')).hexdigest()
            if prova == hashcode:
                tratamento.opcao = opcao
                tratamento.prazo_dt = datetime.today() + timedelta(days=15)
                tratamento.save()
                DefineConsentimentoEvento(empresa, consentimento,
                                          titular.get('nome') + '/' +
                                          titular.get('cpf') + '/' + tratamento.email + ' solicita: ' + opcao)

                url = settings.LGPD_URL + 'sinaliza_tratamento/' + str(tratamento.pk)
                response = requests.get(url, auth=("assist", "123456"))
                if response.status_code == 200:
                    messages.success(request, 'Solicitação enviada com sucesso')

                return HttpResponseRedirect(reverse('lgpd_consulta', kwargs={'cpf': consentimento.cpf}))
            else:
                messages.error(request, 'código incorreto')
    else:
        try:
            lista = lista_2
            url = settings.LGPD_URL + 'cnpj=' + str(consentimento.cliente.cnpj) + '/consentimento/' + str(pk)
            response = requests.get(url, auth=("assist", "123456"))
            if response.status_code == 200:
                obj = json.loads(response.text)
                tratamento = Tratamento()
                tratamento.email = obj['email'] or ''
                tratamento.celular = obj['celular'] or ''
                titular = {
                    'nome': obj['nome'],
                    'cpf': obj['cpf']
                }
        except Exception as e:
            messages.error(request, e)

    if titular.get('cpf'):
        tratamentos = Tratamento.objects.filter(consentimento__cpf=titular.get('cpf')).order_by('id')
    else:
        tratamentos = Tratamento.objects.filter(consentimento=consentimento).order_by('id')

    context['empresa'] = empresa
    context['opcao_id'] = opcao_id
    context['lista'] = lista
    context['hashcode'] = hashcode
    context['titular'] = titular
    context['tratamento'] = tratamento
    context['tratamentos'] = tratamentos
    return render(request, 'lgpd/tratamento.html', context)


def addEventoTratamentoMsg(request, tratamento, msg):
    tratamento.updated_at = datetime.now()
    tratamento.save()

    evento = Evento()
    evento.modulo = 'LGPD'
    evento.descricao = msg
    evento.user = request.user
    evento.cliente = tratamento.consentimento.cliente
    evento.save()

    trata_evento = TratamentoEvento()
    trata_evento.tratamento = tratamento
    trata_evento.evento = evento
    trata_evento.save()


@login_required(login_url='login')
def LgpdResposta(request, pk):
    context = {}
    try:
        tratamento = Tratamento.objects.get(pk=pk)
        if request.POST.get('btn_tratativa') or request.POST.get('btn_encerramento'):
            if request.POST.get('btn_encerramento'):
                tratamento.encerramento_dt = datetime.now()
            addEventoTratamentoMsg(request, tratamento, request.POST.get('txt_conteudo'))

            return HttpResponseRedirect(reverse('url_lgpd_resposta', kwargs={'pk': tratamento.pk}))

        if request.POST.get('btn_email'):
            # addEventoTratamentoMsg(request, tratamento, 'envio de histórico para e-mail de titular')
            lista = TratamentoEvento.objects.filter(tratamento=tratamento).order_by('id')
            lstMsg = []
            for te in lista:
                lstMsg.append(te.evento.created_at.strftime('%d/%m/%Y') + ' ' + te.evento.descricao + "\n")
            send_mail(tratamento, "".join(lstMsg))
            messages.success(request, 'enviado com sucesso')

    except Exception as e:
        messages.error(request, e)

    lista = TratamentoEvento.objects.filter(tratamento=tratamento).order_by('id')
    context['cliente'] = tratamento.consentimento.cliente
    context['tratamento'] = tratamento
    context['lista'] = lista

    return render(request, 'lgpd/resposta.html', context)


def send_mail(tratamento, mensagem):
    subject = 'Histórico de tratativa'
    context = {
        'tratamento': tratamento,
        'mensagem': mensagem
    }
    template_name = 'lgpd/email_resposta_titular.html'
    send_mail_template(
        subject,
        template_name,
        context,
        [tratamento.email]
    )


def getModoLgpd(request):
    if request.POST.get('btn_solicita'):
        return 'SOLICITA'
    elif request.POST.get('btn_enviar_ficha'):
        return 'ANEXO'
    elif request.POST.get('btn_formulario'):
        return 'FICHA'
    else:
        return 'LISTA'


def gravar_consentimento(request, arquivo, cliente, nome, cpf):
    s3_upload_small_files(request.FILES['file'],
                          settings.AWS_STORAGE_BUCKET_NAME,
                          arquivo,
                          request.content_type)
    consentimento = Consentimento()
    consentimento.cpf = cpf
    consentimento.nome = nome
    consentimento.cliente = cliente
    consentimento.created_dt = datetime.now()
    consentimento.autorizado_dt = consentimento.created_dt
    consentimento.updated_dt = consentimento.created_dt
    consentimento.arquivo = arquivo
    consentimento.save()
    DefineConsentimentoEvento(cliente, consentimento, 'consentimento realizado por assinatura em arquivo anexo')


@login_required(login_url='login')
def LgpdControladorConsentimento(request, pk):
    context = {}
    try:
        cliente = Cliente.objects.get(pk=pk)
        lista_consentimento = Consentimento.objects.filter(cliente=cliente).order_by('id').reverse()
        nome = request.POST.get('nome') or ''
        email = request.POST.get('email') or ''
        cpf = request.POST.get('cpf') or ''
        identidade = request.POST.get('identidade') or ''
        nacionalidade = request.POST.get('nacionalidade') or 'Brasileiro'
        estadocivil = request.POST.get('estadocivil') or ''

        finalidade_1 = request.POST.get('finalidade_1') or ''
        finalidade_2 = request.POST.get('finalidade_2') or ''
        finalidade_3 = request.POST.get('finalidade_3') or ''
        consentimentos = request.POST.get('consentimentos') or ''
        modo = getModoLgpd(request)

        if request.method == 'POST':
            form = UploadFileOnlyForm(request.POST, request.FILES)
            if not consentimentos:
                url = settings.LGPD_URL + 'lista_finalidade'
                response = requests.get(url, auth=("assist", "123456"))
                if response.status_code == 200:
                    consentimentos = response.json()
                    request.session['consentimentos'] = consentimentos

            if request.POST.get('btn_upload'):
                if form.is_valid():
                    folder = "clientes/cli-" + str(cliente.cnpj) + "/consentimentos/"
                    file_name = folder + datetime.now().strftime('%Y%m%d_%H%M%S') + "_" + secure_filename(
                        request.FILES['file'].name)
                    gravar_consentimento(request, file_name, cliente, nome, cpf)
                    return HttpResponseRedirect(reverse('url_cliente_consentimento', kwargs={'pk': cliente.pk}))

            if request.POST.get('btn_imprmir'):
                pdf = render_to_pdf('lgpd/termo_consentimento.html', get_data_impressao(request, cliente))
                return HttpResponse(pdf, content_type='application/pdf')

            if request.POST.get('btn_enviar'):
                lista_consentimentos = []
                valor = request.session.get('consentimentos')
                for c in valor:
                    if request.POST.get(c.get('tipo')):
                        lista_consentimentos.append(c.get('tipo'))
                if not lista_consentimentos:
                    consentimentos = request.session.get('consentimentos')
                    raise Exception('selecione pelo menos um consentimento')

                solicitacao = {
                    "operador": {
                        "nome": "Administrador",
                        "email": cliente.email
                    },
                    "tratamentos": get_tratamentos(request),
                    "consentimentos": lista_consentimentos,
                    "titulares": [
                        {
                            "nome": nome,
                            "cpf": cpf,
                            "email": email
                        }
                    ]
                }
                url = settings.LGPD_URL + 'cnpj=' + cliente.cnpj + '/consentimento'
                response = requests.post(url, json.dumps(solicitacao), auth=("assist", "123456"))
                if response.status_code == 200:
                    messages.success(request, 'sucesso na solicitação')
                    request.session['consentimentos'] = None
        else:
            form = UploadFileOnlyForm()

    except Exception as e:
        messages.error(request, e)

    context['form'] = form
    context['modo'] = modo
    context['consentimentos'] = consentimentos
    context['cliente'] = cliente
    context['lista'] = lista_consentimento
    context['nome'] = nome
    context['cpf'] = cpf
    context['email'] = email
    context['identidade'] = identidade
    context['nacionalidade'] = nacionalidade
    context['estadocivil'] = estadocivil
    context['finalidade_1'] = finalidade_1
    context['finalidade_2'] = finalidade_2
    context['finalidade_3'] = finalidade_3

    return render(request, 'lgpd/controlador_consentimento.html', context)
