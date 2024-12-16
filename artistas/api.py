# gestao_eventos/artistas/api.py
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Artista
from .serializers import ArtistaSerializer



class ArtistaViewSet(viewsets.ViewSet):
    def create(self, request):
        # Lógica para criar artista
        serializer = ArtistaSerializer(data=request.data)
        if serializer.is_valid():
            artista = serializer.save()          
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
 
