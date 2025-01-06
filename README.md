✌️Nome do Projeto: APP (Sistema de gerenciamento casa de shows)

1-Criamos um controle de cadastro de pessoas, com os campos de: 
'nome','cpf', 'telefone', 'banco', 'chave pix', 'tipo chave'
'criar msgs', e-mail.

2-Agendamento de: mensagens p watsap, e data e hora.

3-Todo dia a meia noite, o sistema faz uma varredura nas msgs.

4-Monitora as mensagens, e quando tiver; dispara pro cel agendado.

5-Monitorar as msg já enviadas, para não reenvia-las novamente.

6-Criado em Python e Django com o comando(django-admin startproject app).

7-Ambiente virtual: (dhenv).

8-Criado as pastas (accounts, artistas, eventos) como aplicativos.

<<<<<<< HEAD
9-Rodar o projeto: Python manage.py runserver.

10-Fazer login na página do django.

11-Usamos: APScheduler para controlar as msgs pois é suficiente para esse
projeto, e o swager para documentar API.

(O projeto ainda não está pronto, estou finalizando, e organizando o Readme.
=======
4-Usamos: django celery beat, RabbitMQ e vamos usar o swager
pra documentar API.


login=vilce , senha=Gentil123456

 

                     ''' (((ANTES DE ENVIAR O PROJETO, PRA PLATAFORMA E PRO CLIENTE, 'REVISAR O TIME ZONE' e
                     o 'SECRET KEY'))) '''

                    '''AJUSTAR OS  MINUTOS INICIAR SCHEDULER, após os testes'''

 


 

Scheduler started
Mensagem 31 criada e agendada para envio.
Status da mensagem 31 atualizado.


 settings.
 wsgi.py ou asgi.py
 urls.py
 requirements.txt
 manage.py
>>>>>>> penuajuste
