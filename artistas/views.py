from django.contrib import messages
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .forms import ArtistaForm, MessageForm
from . import models, forms
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Artista, Message
from rest_framework import viewsets
from .serializers import ArtistaSerializer, MessageSerializer
from .tasks import enviar_mensagens_agendadas, verificar_status, monitorar_mensagens
import logging 
 

logger = logging.getLogger(__name__)

class ArtistaListView(ListView):
    model = Artista
    template_name = 'artistas_list.html'
    context_object_name = 'artistas'
    
class ArtistaViewSet(viewsets.ModelViewSet):
    queryset = Artista.objects.all()
    serializer_class = ArtistaSerializer
    
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def perform_create(self, serializer):
        message = serializer.save()
        messages.success(self.request, 'Mensagem criada e será enviada conforme o agendamento')#confirmação

@method_decorator(login_required(login_url='login'), name='dispatch')
class ArtistaCreateView(CreateView):
    model = Artista
    template_name = 'artista_create.html'
    form_class = forms.ArtistaForm
    success_url = reverse_lazy('artistas_list')
    
    def form_valid(self, form):
        print("Formulário válido:", form.cleaned_data) 
        response = super().form_valid(form)
        messages.success(self.request, 'Artista criado com sucesso!')
        return response
    
    def form_invalid(self, form):  
        messages.error(self.request, 'Erro ao criar artista. Verifique os dados e tente novamente.')
        return self.render_to_response(self.get_context_data(form=form))
    
class ArtistaDetailView(DetailView):
    model = Artista
    template_name = 'artista_detail.html'
    context_object_name = 'artista'

@method_decorator(login_required(login_url='login'), name='dispatch')
class ArtistaUpdateView(UpdateView):
    model = Artista
    template_name = 'artista_update.html'
    form_class = forms.ArtistaForm
    success_url = reverse_lazy('artista_list')

@method_decorator(login_required (login_url='login'), name='dispatch')
class ArtistaDeleteView(DeleteView):
    model = Artista
    template_name = 'artista_delete.html'
    success_url = reverse_lazy('artista_list')
    
def criar_mensagem(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.artista = artista           
            try:
                message.save() #tenta salvar msg                    
                messages.success(request, 'Mensagem criada com sucesso!')#msg de sucesso
                logger.info(f"Mensagem {message.id} criada e agendada para envio.")
                return redirect('lista_mensagens', pk=artista.id)
            except Exception as e:   #captura qualquer exceção
                logger.error(f"Erro ao criar e agendar mensagem {message.id}: {str(e)}")
                messages.error(request, 'Erro ao criar a mensagem. Tente novamente.') #msg de erro
        else:
            messages.error(request, 'Erro nos dados do formulário. Verifique e tente novamente.') #Msg de erro no form
    else:
        form = MessageForm()
    return render(request, 'mensagens/criar_mensagem_para_artista.html', {'form': form, 'artista': artista})
   
def lista_mensagens(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    mensagens = Message.objects.filter(artista=artista)  
    return render(request, 'mensagens/lista_mensagens.html', {'artista': artista, 'mensagens': mensagens})

def editar_mensagem(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('lista_mensagens', pk=message.artista.id)
    else:
        form = MessageForm(instance=message)
    return render(request, 'mensagens/editar_mensagem.html', {'form': form, 'mensagem': message})
   
def deletar_mensagem(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        message.delete()
        return redirect('lista_mensagens', pk=message.artista.id)
    return render(request, 'mensagens/deletar_mensagem.html', {'mensagem': message})
     
