# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import json
from datetime import datetime, timedelta

from django.db import models
from django.forms import model_to_dict

from compliance.accounts.models import User, CategoriaSAC

CLIENTE_NIVELS = [
    ('N', 'Normal'),
    ('R', 'Restrição'),
    ('C', 'Consulta'),
]

PRIORIDADE_CHOICE = [
    ('BAIXA', 'Baixa'),
    ('MEDIA', 'Média'),
    ('ALTA', 'Alta'),
]

STATUS_CHOICE = [
    ('INICIO', 'Aguardando'),
    ('PRODUCAO', 'Em produção'),
    ('PAUSA', 'Em pausa'),
    ('ANALISE', 'Em análise'),
    ('ENCERRADO', 'Encerrado'),
    ('CANCELADO', 'Cancelado'),
]

MODULO_CHOICE = [
    ('ADMINIST', 'Administrativo'),
    ('FINANCEIRO', 'Financeiro'),
    ('COMERCIA', 'Comercial'),
    ('ATENDIMENTO', 'Atendimento'),
    ('UTIL', 'Utilitário'),
    ('CADASTROS', 'Cadastro'),
    ('CONTRATOS', 'Contrato'),
    ('IPM', 'IPM'),
    ('PILATIS', 'Pilatis'),
    ('COMPLIANCE', 'Compliance'),
    ('VIDA', 'Pilatis Vida'),
    ('BACKUP', 'Backup'),
]

SIM_NAO_CHOICE = [
    (None, ''),
    (True, 'Sim'),
    (False, 'Não'),
]


def tempoSecondsToStr(tempo):
    hours, remainder = divmod(tempo, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


def dt_parser(dt):
    if isinstance(dt, datetime):
        return dt.strftime('%d/%m/%Y %H:%M:%S')


def getStatus(valor):
    for s in STATUS_CHOICE:
        if valor == s[0]:
            return s[1]


def getPrioridade(valor):
    for s in PRIORIDADE_CHOICE:
        if valor == s[0]:
            return s[1]


def getModulo(valor):
    for s in MODULO_CHOICE:
        if valor == s[0]:
            return s[1]


class Cliente(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    fantasia = models.CharField(max_length=100, blank=True, null=True, verbose_name='Fantasia')
    cnpj = models.CharField(max_length=14, unique=True, blank=True, null=False, verbose_name='CNPJ')
    serie = models.CharField(max_length=20, blank=True, null=True, verbose_name='Número Série')
    serie_dt = models.DateTimeField(blank=True, null=True, verbose_name='Dt.Serie')
    nivel = models.CharField(max_length=1, null=True, choices=CLIENTE_NIVELS, verbose_name='Forma de acesso')
    bairro = models.CharField(max_length=50, blank=True, null=True, verbose_name='Bairro')
    cep = models.CharField(max_length=8, blank=True, null=True, verbose_name='CEP')
    email = models.EmailField('E-mail', blank=True, null=True)
    complemento = models.CharField(max_length=35, blank=True, null=True, verbose_name='Complemento')
    logradouro = models.CharField(max_length=150, blank=True, null=True, verbose_name='Logradouro')
    numero = models.IntegerField(verbose_name='Número')
    fone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Fone')
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name='Celular')
    uf = models.CharField(max_length=2, blank=True, null=True, verbose_name='UF')
    observacao = models.TextField(blank=True, null=True, verbose_name='Observação')
    # contato = models.CharField(max_length=100, blank=True, null=True, verbose_name='Contato')
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cidade')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Dt.Inclusão')
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name='Dt.Update')
    data_ult_backup = models.DateTimeField(blank=True, null=True, verbose_name='Dt.Backup')
    monitora = models.BooleanField(choices=SIM_NAO_CHOICE, default=False, blank=True, null=False,
                                   verbose_name='Monitora')
    pode_sms = models.BooleanField(choices=SIM_NAO_CHOICE, default=False, blank=True, null=False,
                                   verbose_name='Envio SMS')
    pode_lgpd = models.BooleanField(choices=SIM_NAO_CHOICE, default=False, blank=True, null=False,
                                    verbose_name='LGPD')
    is_active = models.BooleanField(choices=SIM_NAO_CHOICE, default=True, blank=True, null=False,
                                    verbose_name='Ativo')

    objects = models.Manager()

    def __str__(self):
        return self.nome

    def json(self):
        return model_to_dict(self)

    @property
    def endereco_completo(self):
        return self.logradouro + ', ' + str(
            self.numero) + " " + self.bairro + ", CEP-" + self.cep + " em " + self.cidade + "/" + self.uf

    @property
    def cor(self):
        cor = 'black'
        dias = 0
        if self.data_ult_backup:
            dias = (datetime.today().toordinal() - self.data_ult_backup.date().toordinal())
            if dias > 3:
                cor = 'red'
            elif dias > 2:
                cor = 'orange'
            else:
                cor = 'green'
        else:
            cor = 'red'

        return cor

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']
        db_table = 'cliente'
        permissions = (
            ('MONITORAMENTO', 'Visualizar monitoramento'),
        )


class Evento(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, on_delete=models.CASCADE)
    modulo = models.CharField('Módulo', max_length=30, choices=MODULO_CHOICE, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descricao = models.CharField('Descrição', max_length=500)
    setor = models.CharField('Setor', max_length=100, null=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    objects = models.Manager()

    def json(self):
        cliente = Cliente.objects.get(pk=self.cliente.pk)
        obj = model_to_dict(self)
        obj["cliente"] = cliente.nome
        obj["user"] = self.user.name
        if self.created_at:
            data = datetime.strptime(self.created_at.__str__()[:19], '%Y-%m-%d %H:%M:%S')
            obj["created_at"] = data.strftime('%d/%m/%Y %H:%M:%S')
        return obj

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['created_at', 'cliente']
        db_table = 'evento'


class Documento(models.Model):
    arquivo = models.FileField(upload_to='documentos/')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        db_table = 'documento'


class Tarefa(models.Model):
    documentos = models.ManyToManyField(Documento)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.CASCADE)
    categoria_sac = models.ForeignKey(CategoriaSAC, null=True, on_delete=models.CASCADE)
    identificador = models.BigIntegerField('Tarefa', null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modulo = models.CharField('Módulo', max_length=30, choices=MODULO_CHOICE, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICE, null=True, default='INICIO')
    solicitante = models.CharField('Quem solicitou', max_length=100)
    celular = models.CharField('Celular', max_length=20, null=True)
    email = models.EmailField('E-mail', null=True)
    prioridade = models.CharField('Prioridade', max_length=30, choices=PRIORIDADE_CHOICE, default='BAIXA')
    resumo = models.CharField('Opção de menu', max_length=100)
    demanda = models.TextField('Demanda', null=True)
    tempo_produtivo = models.IntegerField('Tempo Prod.', default=0)
    tempo_ocioso = models.IntegerField('Tempo Prod.', default=0)
    tempo_analise = models.IntegerField('Tempo Analise.', default=0)
    ultimo_tempo = models.DateTimeField('Ult.Hora', null=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Modificado em', auto_now=True, null=True)
    iniciado_dt = models.DateTimeField('Inidicado em', null=True)
    encerrado_dt = models.DateTimeField('Encerrado em', null=True)
    implantado_dt = models.DateTimeField(null=True)

    objects = models.Manager()

    def __str__(self):
        return self.resumo

    def getStatusSAC(self, user):
        return {
            'pode_salvar': (not self.pk or not self.user or self.user == user) and self.status == 'INICIO' and not self.encerrado_dt,
            'pode_observar': self.pk and self.user == user and not self.encerrado_dt and self.iniciado_dt,
            'pode_encaminhar': self.user == user and self.pk and not self.encerrado_dt and self.status != 'PAUSA' and self.iniciado_dt,
            'pode_iniciar': self.pk and not self.encerrado_dt and not self.iniciado_dt,
            'pode_reiniciar': self.pk and not self.encerrado_dt and self.status in 'PAUSA-INICIO',
            'pode_encerrar': self.user == user and self.pk and not self.encerrado_dt and self.iniciado_dt and not self.status == 'PAUSA',
            'pode_pausar': self.user == user and self.pk and self.status != 'PAUSA',
        }

    def addTempoStatus(self, tempo, status):
        if tempo:
            if self.status == 'PRODUCAO':
                if self.tempo_produtivo:
                    self.tempo_produtivo = self.tempo_produtivo + tempo
                else:
                    self.tempo_produtivo = tempo
            elif self.status == 'PAUSA':
                if self.tempo_ocioso:
                    self.tempo_ocioso = self.tempo_ocioso + tempo
                else:
                    self.tempo_ocioso = tempo
            elif self.status == 'ANALISE':
                if self.tempo_analise:
                    self.tempo_analise = self.tempo_analise + tempo
                else:
                    self.tempo_analise = tempo
        self.ultimo_tempo = datetime.now()
        self.status = status

    def dump(self):
        cliente = Cliente.objects.get(pk=self.cliente.pk)
        obj = self.__dict__
        obj['cliente'] = cliente.json()
        obj['usuario'] = self.user
        obj['status'] = getStatus(self.status)
        obj['prioridade'] = getPrioridade(self.prioridade)
        obj['modulo'] = getModulo(self.modulo)
        obj['tempo_produtivo'] = tempoSecondsToStr(self.tempo_produtivo)
        obj['tempo_ocioso'] = tempoSecondsToStr(self.tempo_ocioso)
        obj['tempo_analise'] = tempoSecondsToStr(self.tempo_analise)
        return json.dumps(obj, default=dt_parser)

    @property
    def titulo(self):
        valor = 'Atendimento ' if self.modulo == 'SAC' else 'Tarefa '
        if not self.pk:
            return 'Inclusão de ' + valor
        else:
            for n in STATUS_CHOICE:
                if self.status == n[0]:
                    return valor + n[1].lower()

    @property
    def statusToStr(self):
        for n in STATUS_CHOICE:
            if self.status == n[0]:
                return n[1]

    @property
    def prioridadeToStr(self):
        for n in PRIORIDADE_CHOICE:
            if self.prioridade == n[0]:
                return n[1]

    @property
    def moduloToStr(self):
        for n in MODULO_CHOICE:
            if self.modulo == n[0]:
                return n[1]

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['resumo', 'cliente', 'celular', 'email']
        db_table = 'tarefa'
        permissions = (
            ('IMPLEMENTAR_FUNCIONALIDADE', 'Implementar funcionalidades'),
            ('TESTAR_FUNCIONALIDADE', 'Realizar testes de funcionalidade'),
        )


class TarefaEvento(models.Model):
    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        db_table = 'tarefa_evento'


class UserCliente(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        db_table = 'user_cliente'


class Backup(models.Model):
    arquivo = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    senha = models.CharField(max_length=100, blank=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        db_table = 'backup'

    def __str__(self):
        return self.arquivo
