import logging
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import re 
from validate_docbr import CPF
 
 
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
    created_at = models.DateTimeField(auto_now_add=True) 
    
    def clean(self):
        super().clean()
        if self.tipo_chave_pix == 'cpf' and not re.match(r'^\d{11}$', self.chave_pix):
            raise ValidationError({'chave_pix': 'A chave Pix deve ser um CPF válido (11 dígitos).'})
        if self.tipo_chave_pix == 'cnpj' and not re.match(r'^\d{14}$', self.chave_pix):
            raise ValidationError({'chave_pix': 'A chave Pix deve ser um CNPJ válido (14 dígitos).'})
        if self.tipo_chave_pix == 'email' and '@' not in self.chave_pix:
            raise ValidationError({'chave_pix': 'A chave Pix deve ser um endereço de e-mail válido.'})
        if self.tipo_chave_pix == 'cel' and not re.match(r'^\d{2}\d{8,9}$', self.chave_pix):
            raise ValidationError({'chave_pix': 'A chave Pix deve ser um número de celular válido com código do país.'})
        #validando telefone
        if self.telefone and not re.match(r'^\+\d{1,3}\d{9,15}$', self.telefone):
            raise ValidationError({'telefone': 'O telefone deve incluir o código do país e ser válido.'})
        #validando cpf
        cpf_validator = CPF()
        if not cpf_validator.validate(self.cpf):
            raise ValidationError({'cpf': 'CPF inválido.'})
    

    def save(self, *args, **kwargs):
        self.full_clean()  # Garante validações ao salvar
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.nome   
    """
    Verificar se o artista tem informações incompletas ou inativas.
    """
    def deve_ser_atualizado(self):
        campos_obrigatorios = [self.telefone, self.email]
        return any(campo is None or campo == '' for campo in campos_obrigatorios)
    """
    Atualiza o status do artista.
    """ 
    def atualizar_status(self):
        if self.deve_ser_atualizado():
            logger.info(f"Artista {self.id} com informações incompletas.")
            self.save()
         

class Message(models.Model):
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    conteudo = models.TextField()
    scheduled_date = models.DateTimeField(auto_now_add=True, verbose_name="Data Agendada")
    send_date = models.DateTimeField(default=timezone.now, verbose_name="Data de Envio")
    sent = models.BooleanField(default=False, verbose_name="Enviada")
    
         
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
        if self.deve_ser_atualizado():
            logger.warning(f"Mensagem {self.id} está atrasada.")                    
            self.sent = False  #Assegura q mensagem permanece ñ enviada.
            self.save()
                                    
         
            
    @property
    def status(self):
        #retorna o status atual da msg
        if self.sent:
            return "Enviada"
        if not self.sent and self.send_date < timezone.now():
            return "Atrasada"
        return "Pendente"
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"