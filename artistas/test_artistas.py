import pytest
from unittest.mock import MagicMock, patch 
from django.utils import timezone
from django.utils.timezone import now, timedelta 
from artistas.tasks import (
    enviar_mensagens_agendadas,
    monitorar_mensagens,
    verificar_status,
    iniciar_scheduler,
    scheduler,
)
from artistas.models import Artista, Message
from datetime import datetime


@pytest.mark.django_db
@patch('artistas.tasks.Message.objects.filter')
@patch('artistas.tasks.Artista.objects.all')
@patch('artistas.tasks.logger')
def test_monitorar_mensagens(mock_logger, mock_all_artistas, mock_filter):
    # Criando o mock para o Artista e a Message
    mock_artista = MagicMock(spec=Artista)
    mock_message = MagicMock(spec=Message)

    # Definindo a data atual com precisão reduzida
    agora = timezone.now().replace(microsecond=0)

    # Simulando o retorno do banco de dados
    mock_message.send_date = agora
    mock_message.sent = False
    mock_message.deve_enviar.return_value = True  # Mensagem deve ser enviada
    mock_message.enviar.side_effect = Exception("Erro ao enviar a mensagem")  # Simulando erro no envio

    # Simulando que temos 1 artista e 1 mensagem
    mock_artista.id = 1
    mock_all_artistas.return_value = [mock_artista]  # Simulando que temos 1 artista
    mock_filter.return_value = [mock_message]  # Simulando que temos uma mensagem para enviar
    
    from artistas.tasks import monitorar_mensagens
    monitorar_mensagens()

    # Chamando a função de envio de mensagens
    enviar_mensagens_agendadas()

    # Verificando se o filtro foi chamado corretamente
    mock_filter.assert_called_once_with(
        artista=mock_artista, send_date__lte=agora, sent=False)

    # Verificando se o logger foi chamado
    mock_logger.error.assert_called_once_with(
        f"Erro ao enviar mensagem {mock_message.id} para o artista {mock_artista.id}: Erro ao enviar a mensagem"
    )

 
@pytest.mark.django_db
@patch('artistas.tasks.Message.objects.filter')
@patch('artistas.tasks.Artista.objects.all')
@patch('artistas.tasks.logger')
def test_enviar_mensagens_agendadas(mock_logger, mock_all_artistas, mock_filter):
    # Criando um artista real no banco de dados
    artista = Artista.objects.create(
        nome="Artista Teste", cpf="123.456.789-00", banco="Banco Teste", chave_pix="123456", tipo_chave_pix="cel"
    )

    # Criando uma mensagem real no banco de dados
    message = Message.objects.create(
        artista=artista, conteudo="Conteúdo da mensagem", send_date=timezone.now(), sent=False
    )

    # Mockando os retornos
    mock_all_artistas.return_value = [artista]
    mock_filter.return_value = [message]

    # Chamando a função de envio
    enviar_mensagens_agendadas()

    # Verificações
    message.refresh_from_db()  # Recarrega do banco para validar mudanças
    assert message.sent is True  # Verifica se o campo foi atualizado
    mock_logger.error.assert_not_called()  # Verifica que não houve 

@pytest.mark.django_db
@patch('artistas.tasks.Message.objects.filter')
@patch('artistas.tasks.Artista.objects.all')
@patch('artistas.tasks.logger')
def test_mensagem_nao_enviada(mock_logger, mock_all_artistas, mock_filter):
    # Criando o mock para a mensagem
    mock_artista = MagicMock(spec=Artista)
    mock_message = MagicMock(spec=Message)

    # Simulando o cenário onde a mensagem não deve ser enviada
    mock_message.send_date = timezone.now()
    mock_message.sent = False
    mock_message.deve_enviar.return_value = False  # Mensagem não deve ser enviada
    mock_message.enviar.return_value = None

    mock_filter.return_value = [mock_message]  # Simulando que temos uma mensagem para enviar

    # Chamando a função de envio de mensagens
    enviar_mensagens_agendadas()

    # Verificando se o método 'enviar' não foi chamado
    mock_message.enviar.assert_not_called()

    # Verificando se o log não foi chamado para essa mensagem
    mock_logger.info.assert_not_called()
    
@pytest.mark.django_db
@patch('artistas.tasks.Message.objects.filter')
@patch('artistas.tasks.Artista.objects.all')
@patch('artistas.tasks.logger')
def test_monitorar_mensagens(mock_logger, mock_all_artistas, mock_filter):
    # Criando o mock para o Artista e a Message
    mock_artista = MagicMock(spec=Artista)
    mock_message = MagicMock(spec=Message)
    
    mock_artista.id = 1 
    mock_message.id = 123

    # Definindo a data atual
    agora = timezone.now()
    
    

    # Simulando o retorno do banco de dados
    mock_message.send_date = agora
    mock_message.sent = False
    mock_message.deve_enviar.return_value = True  # Mensagem deve ser enviada
    mock_message.enviar.side_effect = Exception("Erro ao enviar a mensagem")  # Simulando erro no envio   
 

    # Simulando que temos 1 artista e 1 mensagem  
    mock_all_artistas.return_value = [mock_artista]  # Simulando que temos 1 artista
    mock_filter.return_value = [mock_message]  # Simulando que temos uma mensagem para enviar
    # Chamando a função de envio de mensagens
    enviar_mensagens_agendadas()

    # Verificando se o filtro foi chamado corretamente
    mock_filter.assert_called_once_with(artista=mock_artista, send_date__lte=agora, sent=False)

     
    # Verificando se o método 'enviar' foi chamado
    mock_message.enviar.assert_called_once()
    
    # Verificando se o log de erro foi chamado
    mock_logger.error.assert_called_once_with(
        f"Erro ao enviar mensagem {mock_message.id} para o artista {mock_artista.id}: Erro ao enviar a mensagem")
    
    # verificando se a msg foi marcada como enviada    
    mock_message.save.assert_not_called()

@pytest.mark.django_db
@patch('artistas.tasks.Message.objects.filter')
@patch('artistas.tasks.Artista.objects.all')
@patch('artistas.tasks.logger')
def test_monitorar_mensagens_erro(mock_logger, mock_all_artistas, mock_filter):
    # Criando o mock para o Artista e a Message
    mock_artista = MagicMock(spec=Artista)
    mock_message = MagicMock(spec=Message)
    
    # Definindo a data atual (agora)
    agora = timezone.now()

    # Simulando o cenário onde a mensagem não pode ser enviada (erro)
    mock_message.send_date = timezone.now()
    mock_message.sent = False
    mock_message.deve_enviar.return_value = True  # Mensagem deve ser enviada
    mock_message.enviar.side_effect = Exception("Erro ao enviar a mensagem")  # Simulando erro no envio

    # Simulando que temos 1 artista e 1 mensagem
    mock_artista.id = 1
    mock_all_artistas.return_value = [mock_artista]
    mock_filter.return_value = [mock_message]  # Simulando que temos uma mensagem para enviar

    # Chamando a função de envio de mensagens
    enviar_mensagens_agendadas()

    # Verificando se o filtro foi chamado corretamente
    mock_filter.assert_called_once_with(artista=mock_artista, send_date__lte=agora, sent=False)

    # Verificando se o método 'enviar' foi chamado na mensagem
    mock_message.enviar.assert_called_once()

    # Verificando se o log de erro foi chamado
    mock_logger.error.assert_called_once_with(f"Erro ao enviar mensagem {mock_message.id} para o artista {mock_artista.id}: Erro ao enviar a mensagem")

    # Verificando se a mensagem não foi marcada como enviada
    mock_message.save.assert_not_called()

@pytest.mark.django_db
@patch('artistas.tasks.Message.objects.filter')
@patch('artistas.tasks.Artista.objects.all')
@patch('artistas.tasks.logger')
def test_falha_na_funcao_enviar(mock_logger, mock_all_artistas, mock_filter):
    # Criando o mock para Artista e Message
    mock_artista = MagicMock(spec=Artista)
    mock_message = MagicMock(spec=Message)

    # Configurando atributos da mensagem
    mock_message.id = 1
    mock_message.send_date = timezone.now()
    mock_message.sent = False
    mock_message.deve_enviar.return_value = True
    mock_message.enviar.side_effect = Exception("Erro simulado ao enviar mensagem")  # Simula a falha no envio

    # Configurando o retorno dos mocks
    mock_all_artistas.return_value = [mock_artista]
    mock_filter.return_value = [mock_message]

    # Chamando a função que testa o envio
    enviar_mensagens_agendadas()

    # Verificando se o método 'enviar' foi chamado, mas causou um erro
    mock_message.enviar.assert_called_once()

    # Validando que o erro foi capturado no logger
    mock_logger.error.assert_called_once_with(
        f"Erro ao enviar mensagem {mock_message.id} para o artista {mock_artista.id}: Erro simulado ao enviar mensagem"
    )

    # Confirmando que o método 'save' NÃO foi chamado, pois o envio falhou
    mock_message.save.assert_not_called()

 
@pytest.mark.django_db
@patch('artistas.tasks.Message.objects.filter')
@patch('artistas.tasks.Artista.objects.all')
@patch('artistas.tasks.logger')
def test_falha_em_deve_enviar(mock_logger, mock_all_artistas, mock_filter):
    # Criando mock para Artista e Message
    mock_artista = MagicMock(spec=Artista)
    mock_message = MagicMock(spec=Message)

    # Configurando atributos do mock
    mock_message.id = 1
    mock_message.send_date = timezone.now()
    mock_message.sent = False
    mock_message.deve_enviar.side_effect = Exception("Erro simulado em deve_enviar")

    # Configurando o retorno dos mocks
    mock_all_artistas.return_value = [mock_artista]
    mock_filter.return_value = [mock_message]

    # Chamando a função de envio de mensagens
    enviar_mensagens_agendadas()

    # Verificando se o método 'deve_enviar' foi chamado e falhou
    mock_message.deve_enviar.assert_called_once()
    mock_logger.error.assert_called_once_with(
        f"Erro ao enviar mensagem {mock_message.id} para o artista {mock_artista.id}: Erro simulado em deve_enviar"
    )

    # Garantindo que a mensagem não foi marcada como enviada
    mock_message.save.assert_not_called()

@pytest.mark.django_db
@patch('artistas.models.Artista.deve_ser_atualizado', side_effect=Exception("Erro simulado em deve_ser_atualizado"))
@patch('artistas.tasks.logger')
def test_falha_em_deve_ser_atualizado(mock_logger, mock_deve_ser_atualizado):
     # Criando uma instância real de Artista
    artista = Artista.objects.create(nome="Artista Teste")
    messages = Message.objects.filter(artista=artista, send_date__lte=timezone.now())

    # Chamando a função de verificação de status
    verificar_status()

    # Verificando se 'deve_ser_atualizado' foi chamado e falhou
    mock_deve_ser_atualizado.assert_called_once_with()
    mock_logger.error.assert_called_once_with(
        f"Erro ao atualizar o status do artista {artista.id}: Erro simulado em deve_ser_atualizado"
    )

@pytest.mark.django_db
@pytest.mark.django_db
def test_verificar_status():
    # Criando um objeto real de Artista no banco de dados
    artista = Artista.objects.create(
        nome="Teste Artista",
        cpf="123.456.789-00",
        telefone=None,
        banco="Banco Teste",
        tipo_chave_pix="cel",
        chave_pix="123456789",
        email=None  # Artista incompleto para ser atualizado
    )

    # Chamando a função verificar_status
    verificar_status()

    # Atualizando a instância do banco
    artista.refresh_from_db()

    # Verificando se o status foi atualizado (telefone ou email ausente)
    assert artista.telefone is None  # Simula a lógica de 'deve_ser_atualizado'
    assert artista.email is None
@pytest.mark.django_db
def test_integracao_envio_mensagens_com_banco():
    # Criando artistas e mensagens no banco de dados
    artista1 = Artista.objects.create(nome="Artista 1", telefone="123456789", email="teste1@email.com", cpf="123.456.789-01")
    artista2 = Artista.objects.create(nome="Artista 2", telefone="987654321", email="teste2@email.com", cpf="987.654.321-00")
    
    mensagem1 = Message.objects.create(
        artista=artista1,
        conteudo="Mensagem 1",
        send_date=now() - timedelta(minutes=5),  # Data passada
        sent=False
    )
    mensagem2 = Message.objects.create(
        artista=artista2,
        conteudo="Mensagem 2",
        send_date=now() + timedelta(minutes=5),  # Data futura
        sent=False
    )

    # Chamando a função de envio de mensagens
    enviar_mensagens_agendadas()

    # Verificando o status das mensagens no banco de dados
    mensagem1.refresh_from_db()
    mensagem2.refresh_from_db()

    # Mensagem 1 deve ter sido enviada
    assert mensagem1.sent is True
    assert mensagem1.send_date <= now()

    # Mensagem 2 não deve ter sido enviada
    assert mensagem2.sent is False
    assert mensagem2.send_date > now()
    
@pytest.mark.django_db
@patch('artistas.tasks.enviar_mensagens_agendadas')
@patch('artistas.tasks.verificar_status')
def test_scheduler_em_segundo_plano(mock_verificar_status, mock_enviar_mensagens_agendadas):
    # Parar o scheduler se já estiver rodando
    if scheduler.state == 1:  # 1 significa "RUNNING"
        scheduler.shutdown(wait=False)    
        
    # Limpando jobs existentes no scheduler
    scheduler.remove_all_jobs()
    
    # Iniciando o scheduler
    iniciar_scheduler()
    
    #Recuper jobs registrados
    jobs = scheduler.get_jobs()    

     
    # Verificando se os jobs foram adicionados corretamente
    assert len(jobs) == 2, f"Esperado 2 jobs, mas encontrado {len(jobs)}"   
    assert any(job.func == mock_enviar_mensagens_agendadas for job in jobs), "Job enviar_mensagens_agendadas não registrado."
    assert any(job.func == mock_verificar_status for job in jobs), "Job verificar_status não registrado."

    # Simulando a execução dos jobs
    for job in jobs:
        job.func()

    # Verificando se as funções associadas aos jobs foram chamadas
    mock_enviar_mensagens_agendadas.assert_called_once()
    mock_verificar_status.assert_called_once()
    
    #Parar o scheduler após o teste
    scheduler.shutdown(wait=False)
    
@pytest.mark.django_db
@patch('artistas.tasks.Message.objects.filter')
@patch('artistas.tasks.Artista.objects.all')
@patch('artistas.tasks.logger')
def test_monitorar_mensagens_erro(mock_logger, mock_all_artistas, mock_filter):
    # Criando o mock para o Artista e a Message
    mock_artista = MagicMock(spec=Artista)
    mock_message = MagicMock(spec=Message)

    # Usando uma variável compartilhada para timezone.now()
    agora = timezone.now()

    # Simulando o cenário onde a mensagem não pode ser enviada (erro)
    mock_message.send_date = agora
    mock_message.sent = False
    mock_message.deve_enviar.return_value = True  # Mensagem deve ser enviada
    mock_message.enviar.side_effect = Exception("Erro ao enviar a mensagem")  # Simulando erro no envio

    # Simulando que temos 1 artista e 1 mensagem
    mock_artista.id = 1
    mock_all_artistas.return_value = [mock_artista]
    mock_filter.return_value = [mock_message]  # Simulando que temos uma mensagem para enviar

    # Chamando a função de envio de mensagens
    enviar_mensagens_agendadas()

    # Verificando se o filtro foi chamado corretamente
    mock_filter.assert_called_once_with(artista=mock_artista, send_date__lte=agora, sent=False)

    # Verificando se o método 'enviar' foi chamado na mensagem
    mock_message.enviar.assert_called_once()

    # Verificando se o log de erro foi chamado
    mock_logger.error.assert_called_once_with(
        f"Erro ao enviar mensagem {mock_message.id} para o artista {mock_artista.id}: Erro ao enviar a mensagem"
    )
    
@pytest.mark.django_db
@patch('artistas.tasks.scheduler')
def test_iniciar_scheduler(mock_scheduler):
    # Simula o estado inicial do scheduler
    mock_scheduler.state = 0  # Simulando estado inativo

    # Limpando jobs existentes (mockado)
    mock_scheduler.remove_all_jobs.return_value = None

    # Chamando a função iniciar_scheduler
    iniciar_scheduler()

    # Verificando se o scheduler foi iniciado
    mock_scheduler.start.assert_called_once()

    # Verificando se os jobs foram adicionados corretamente
    mock_scheduler.add_job.assert_any_call(enviar_mensagens_agendadas, 'interval', minutes=1)
    mock_scheduler.add_job.assert_any_call(verificar_status, 'interval', minutes=1)