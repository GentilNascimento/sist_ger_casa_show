# gestao_eventos/artistas/serializers.py
from rest_framework import serializers
from .models import Artista, Message



class ArtistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artista
        fields = ['id', 'nome', 'cpf', 'telefone', 'banco', 'tipo_chave_pix', 'chave_pix', 'email']
        
class MessageSerializer(serializers.ModelSerializer):
    artista = ArtistaSerializer()
    class Meta:
        model = Message
        fields = ['id', 'artista', 'conteudo', 'send_date', 'sent']
        
    def create(self, validated_data):
        artista_data = validated_data.pop('artista')
        artista, created = Artista.objects.get_or_create(**artista_data)
        message = Message.objects.create(artista=artista, **validated_data)
        return message




