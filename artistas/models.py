import logging
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

logger = logging.getLogger('artistas')


TIPO_CHAVE_CHOICES = [
    ('cel', 'Celular'),
    ('cnpj', 'CNPJ'),
    ('email', 'E-mail'), 
    ('cpf', 'CPF'),
]

class Artista(models.Model):

    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    banco = models.CharField(max_length=100)
    tipo_chave_pix = models.CharField(max_length=10, choices=TIPO_CHAVE_CHOICES, default='cel')
    chave_pix = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True) 
     

    def __str__(self):
        return self.nome
    
    def deve_ser_atualizado(self):
        """
        Lógica para determinar se o status do artista deve ser atualizado.
        Exemplo: Verificar se o artista tem informações incompletas ou inativas.
        """
        return not self.telefone or not self.email  # Atualize conforme a lógica de negócio.

    def atualizar_status(self):
        """
        Atualiza o status do artista.
        Exemplo: Marcar o artista como inativo se ele não tiver informações completas.
        """
        try:
            if self.deve_ser_atualizado():
                # Aqui pode haver lógica adicional, como definir atributos ou status.
                self.save()
        except Exception as e:
            logger.error(f"Erro ao atualizar status do artista {self.id}: {e}")
            raise e

class Message(models.Model):
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    conteudo = models.TextField()
    scheduled_date = models.DateTimeField(auto_now_add=True, verbose_name="Data Agendada")
    send_date = models.DateTimeField(default=timezone.now, verbose_name="Data de Envio")
    sent = models.BooleanField(default=False, verbose_name="Enviada")
    
    def clean(self):
        super().clean()
        if self.send_date.year < 1000 or self.send_date.year > 9999:
            raise ValidationError({'send_date': "O ano deve ter exatamente 4 dígitos."}) 
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Chama o método clean() para validação
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"Mensagem para {self.artista.nome} agendada para {self.send_date}"
    #A mensagem deve ser enviada se a data de envio é menor ou igual ao horário atual
    #e ainda não foi marcada como enviada.
    def deve_enviar(self):
        return self.send_date <= timezone.now() and not self.sent
    
    #lógica de envio das msg.
    def enviar(self):
        if self.sent:
            return  #impede o reenvio        
        try:
            #Simula o envio da msg
            self.sent = True   #atualiza o status p envio
            self.save()   #persiste a alteração no Bd
            
            logger.info(f"Mensagem ID {self.id} enviada com sucesso para o artista {self.artista.nome}.")
             
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem ID {self.id}: {e}")
            raise e #propaga a exceção p depuração
         
            
    def deve_ser_atualizado(self):
    # Verifica se a mensagem não foi enviada e se a data de envio passou.
        return not self.sent and self.send_date < timezone.now() 
       
    def atualizar_status(self):
            #marca a msg como atrasada se passou a data, e não enviou        
            try:
                if self.deve_ser_atualizado():                    
                    self.sent = False  #Assegura q mensagem não enviadas, sejam tratadas corretamente.
                    self.save()
                                    
            except Exception as e:
                logger.error(f"Erro ao atualizar o status da mensagem {self.id}: {e}")
                raise e
            
    @property
    def status(self):
        if self.sent:
            return "Enviada"
        elif self.deve_ser_atualizado():
            return "Atrasada"
        return "Pendente"
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"