from django.contrib import admin
from .models import Artista, Message

@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'banco', 'tipo_chave_pix', 'chave_pix',)
    search_fields = ('nome', 'cpf', 'telefone',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('artista', 'send_date', 'sent')
    list_filter = ('sent', 'send_date')
    search_fields = ('artista__nome', 'conteudo')
    
