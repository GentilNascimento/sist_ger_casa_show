# artistas/tasks.py
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.conf import settings
from .models import Artista, Message
import logging
from app.scheduler import scheduler 
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setLevel(logging.INFO)  # Suprime logs de adição de jobs, mas mantém logs importantes

 
 # Função para enviar mensagens agendadas
def enviar_mensagens_agendadas():
    agora = timezone.now()
    artistas = Artista.objects.all()
    for artista in artistas:
        messages = Message.objects.filter(artista=artista, send_date__lte=agora, sent=False)
         
        for message in messages:
            try:
                # Verifica e envia a mensagem programada
                if message.deve_enviar():
                    message.enviar()  #simula envio da msg 
                    logger.info(f"Mensagem {message.id} enviada com sucesso para o artista {artista.nome}.")                    
            except Exception as e:                 
                logger.error(f"Erro ao enviar mensagem {message.id} para o artista {artista.nome}: {e}")  
                
               
def monitorar_mensagens():
    messages = Message.objects.filter(sent=False)
    agora = timezone.now()

    for message in messages:
        if message.send_date <= agora and not message.sent:
            try:
                enviar_mensagens_agendadas()
                
            except Exception as e:
                logger.error(f"Erro ao tentar enviar mensagem {message.id}: {e}")
                message.refresh_from_db()

# Função para atualizar status dos artistas e eventos, se necessário
def verificar_status():
    artistas = Artista.objects.all()
    for artista in artistas:
        try:
            if artista.deve_ser_atualizado():
                artista.atualizar_status()
                artista.save()
        except Exception as e:
            logger.error(f"Erro ao atualizar o status do artista {artista.id}: {e}")

        messages = Message.objects.filter(artista=artista)
        for message in messages:
            if message.deve_ser_atualizado():
                message.atualizar_status()
                message.save()
                logger.info(f"Status da mensagem {message.id} atualizado.")

 

def iniciar_scheduler():
    # Verifica se o sistema está em modo de 
      
    is_testing = os.environ.get("PYTEST_CURRENT_TEST", None) is not None

    # Adiciona os jobs com intervalos ajustados para testes ou produção
    scheduler.add_job(enviar_mensagens_agendadas, 'interval', minutes=1 if is_testing else 5)
    scheduler.add_job(verificar_status, 'interval', minutes=1 if is_testing else 10)

    # Inicia o scheduler
    scheduler.start()
    logger.info("APScheduler iniciado para tarefas de mensagens e verificação de status.")
     
 
