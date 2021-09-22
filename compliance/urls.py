"""compliance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from compliance.accounts.views import userEdit, userRegister, userList, \
    atendimentoSAC, atendimentoEditSAC, SAC_avulso, SAC_cliente, clienteSerie, encerramento, userPassword
from compliance.atendimento.views import ocorrencia, ocorrenciaEdit, OcorrenciaRemove, atendimentoList, atendimentoAdd, \
    atendimentoEdit
from compliance.core.views import home, ClienteListView, clienteNew, clienteUpdate, ClienteTarefaNew, \
    ClienteTarefaList, ClienteTarefaEdit, ClienteEventoList, MonitorBackupNew, acessos, TarefaLista, \
    TarefaImprimir, TarefaReopen, download, ClienteAWS, ClienteFolderAWS, ClienteBackup, ClienteUsuario, \
    downloadObjectS3, TarefaAnexo, TarefaRemoveAnexo, GeradorRelatorio
from compliance.lgpd.views import LgpdConsentimento, LgpdConsultaTitular, LgpdTratamentoId, \
    LgpdControladorConsentimento, LgpdControladorTratamento, LgpdConsultaTitularCPF, LgpdTratamentoDados, LgpdResposta
from compliance.pessoa.views import ClienteContatoView, ContatoView, ContatoRemoveView, ImprimirCadastroCliente

urlpatterns = [
                  path('grappelli/', include('grappelli.urls')),
                  path('sac/', atendimentoSAC, name='url_sac_list'),
                  path('sac/avulso/', SAC_avulso, name='url_sac_avulso'),
                  path('sac/cliente/<int:pk>', SAC_cliente, name='url_sac_cliente'),
                  path('sac/<int:pk>/', atendimentoEditSAC, name='url_sac_edit'),
                  path('user/', userList, name='url_user_list'),
                  path('user/add/', userRegister, name='url_user_add'),
                  path('user/<int:pk>/', userEdit, name='url_user_edit'),
                  path('password/', userPassword, name='password'),

                  path('entrar/', auth_views.LoginView.as_view(
                      redirect_authenticated_user=True,
                      template_name='accounts/login.html'), name='login'),
                  path('logout/', auth_views.LogoutView.as_view(
                      template_name='core/home.html'), name='logout'),
                  path('sair/', encerramento, name='url_sair'),

                  path('cliente/', ClienteListView, name='url_cliente_list'),
                  path('cliente/add/', clienteNew, name='url_cliente_new'),
                  path('cliente/<int:pk>/', clienteUpdate, name='url_cliente_update'),
                  path('cliente/<int:pk>/contato', ClienteContatoView, name='url_cliente_contato'),
                  path('cliente/<int:pk>/usuario', ClienteUsuario, name='url_cliente_usuario'),
                  path('cliente/<int:pk>/consentimento', LgpdControladorConsentimento,
                       name='url_cliente_consentimento'),
                  path('cliente/<int:pk>/tratamento', LgpdControladorTratamento, name='url_cliente_tratamento'),
                  path('cliente/<int:pk>/backup=<str:arquivo>', ClienteBackup, name='url_cliente_backup'),
                  path('cliente/<int:pk>/s3', ClienteAWS, name='url_cliente_aws'),
                  path('cliente/<int:pk>/s3/<str:folder>', ClienteFolderAWS, name='url_cliente_folder_aws'),
                  path('cliente/<int:pk>/serie', clienteSerie, name='url_cliente_serie'),
                  path('cliente/<int:pk>/tarefa/', ClienteTarefaList, name='url_cliente_tarefa'),
                  path('cliente/<int:pk>/tarefa/add/', ClienteTarefaNew, name='url_cliente_tarefa_new'),
                  path('cliente/<int:pk>/evento/', ClienteEventoList, name='url_cliente_evento'),
                  path('contato/<int:pk>/', ContatoView, name='url_contato'),
                  path('contato/<int:pk>/remove', ContatoRemoveView, name='url_contato_remove'),
                  path('fichacliente/<int:pk>/', ImprimirCadastroCliente, name='url_ficha_cliente'),

                  path('tarefa/', TarefaLista, name='url_tarefa_list'),
                  path('tarefa/<int:pk>/', ClienteTarefaEdit, name='url_cliente_tarefa_edit'),
                  path('tarefa/<int:pk>/imprimir', TarefaImprimir, name='url_tarefa_imprimir'),
                  path('tarefa/<int:pk>/reopen', TarefaReopen, name='url_tarefa_reopen'),
                  path('tarefa/<int:pk>/anexo', TarefaAnexo, name='url_tarefa_anexo'),
                  path('tarefa/<int:pk>/anexo/remove=<str:nome>', TarefaRemoveAnexo, name='url_tarefa_anexo_remove'),

                  path('download/<int:pk>', download, name='url_download'),
                  path('s3/<str:nome>', downloadObjectS3, name='url_download_s3'),
                  path('admin/', admin.site.urls),
                  path('monitor/', MonitorBackupNew, name='monitor'),
                  path('', home, name='home'),
                  path('acessos', acessos, name='acessos'),

                  path('lgpd/consentimento/<int:pk>', LgpdConsentimento, name='lgpd_consentimento'),
                  path('minha_lgpd', LgpdConsultaTitular, name='minha_lgpd'),
                  path('minha_lgpd/cpf=<str:cpf>', LgpdConsultaTitularCPF, name='lgpd_consulta'),
                  path('lgpd/tratamento/id=<int:pk>', LgpdTratamentoId, name='lgpd_tratamento_id'),
                  path('lgpd/dados/id=<int:pk>', LgpdTratamentoDados, name='lgpd_dados_id'),
                  path('lgpd/resposta/id=<int:pk>', LgpdResposta, name='url_lgpd_resposta'),

                  path('ocorrencia/', ocorrencia, name='url_ocorrencia'),
                  path('ocorrencia/<str:uuid>', ocorrenciaEdit, name='url_ocorrencia_edit'),
                  path('ocorrencia/<str:uuid>/remove/', OcorrenciaRemove, name='url_ocorrencia_remove'),
                  path('atendimento/', atendimentoList, name='url_atendimento'),
                  path('atendimento/add/', atendimentoAdd, name='url_atendimento_new'),
                  path('atendimento/<str:uuid>/', atendimentoEdit, name='url_atendimento_edit'),

                  path('relatorio/', GeradorRelatorio, name='url_relatorio'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
