import pytest
from django.utils import timezone
from eventos.models import Evento
from artistas.models import Artista
from unittest.mock import patch


@pytest.fixture
def artista():
    return Artista.objects.create(
        nome="Event Artist",
        cpf="123.456.789-00",
        telefone="(11) 98765-4321",
        banco="Test Bank",
        tipo_chave_pix="cel",
        chave_pix="987654321",
        email="artist@test.com"
    )


@pytest.fixture
@patch("eventos.signals.scheduler")
def evento(mock_scheduler, artista):
    return Evento.objects.create(
        artista=artista,
        data=timezone.now().date(),
        horario=timezone.now().time(),
        descricao="Descrição do evento",
        scheduled_date=timezone.now(),
        send_date=timezone.now()
    )

@pytest.mark.django_db
@patch("eventos.signals.scheduler")
def test_evento_cria_tarefa_agendada(mock_scheduler, artista):
    mock_scheduler.add_job.return_value = None
    evento = Evento.objects.create(
        artista=artista,
        data=timezone.now().date(),
        horario=timezone.now().time(),
        descricao="Teste de agendamento",
        scheduled_date=timezone.now(),
        send_date=timezone.now()
    )
    mock_scheduler.add_job.assert_called_once()
    args, kwargs = mock_scheduler.add_job.call_args
    assert kwargs["id"] == f"evento-{evento.id}"

@pytest.mark.django_db
@patch("eventos.signals.scheduler")
def test_evento_remove_tarefa_agendada(mock_scheduler, artista):
    """
    Testa se a exclusão de um evento remove a tarefa agendada.
    """
    evento = Evento.objects.create(
        artista=artista,
        data=timezone.now().date(),
        horario=timezone.now().time(),
        descricao="Descrição de teste",
        scheduled_date=timezone.now(),
        send_date=timezone.now()
    )
    evento_id = evento.id
    evento.delete()
    mock_scheduler.remove_job.assert_called_once_with(f"evento-{evento_id}")   

@pytest.mark.django_db  
@patch("eventos.signals.scheduler") 
def test_evento_str(mock_scheduler, evento):
    """
    Testa a representação em string do modelo Evento.
    """
    expected_str = f"{evento.artista.nome} - {evento.formatted_data()} {evento.formatted_horario()}"
    assert str(evento) == expected_str

@pytest.mark.django_db
def test_evento_formatted_data(evento):
    """
    Testa o método formatted_data do modelo Evento.
    """
    formatted_date = evento.data.strftime('%d-%m-%Y')
    assert evento.formatted_data() == formatted_date

@pytest.mark.django_db
def test_evento_formatted_horario(evento):
    """
    Testa o método formatted_horario do modelo Evento.
    """
    formatted_time = evento.horario.strftime('%H-%M')
    assert evento.formatted_horario() == formatted_time
    
def test_scheduler_instance():
    from app.scheduler import scheduler
    assert hasattr(scheduler, "add_job"), "O scheduler não possui o método 'add_job'"

