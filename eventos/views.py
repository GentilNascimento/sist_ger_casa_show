from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.views.generic import DetailView
from . import models, forms
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

class EventoListView(ListView):
    model = models.Evento
    template_name = 'evento_list.html'
    context_object_name = 'eventos'
    paginate_by = 6


@method_decorator(login_required(login_url= 'login'), name = 'dispatch')
class EventoCreateView(CreateView):
    model = models.Evento
    template_name = 'evento_create.html'
    form_class = forms.EventoForm
    success_url = reverse_lazy('evento_list')
    
    def form_valid(self, form):
        print("Formulário é válido, salvando evento...")
        response = super().form_valid(form)
        messages.success(self.request, 'Evento criado com sucesso!')
        return response
    
    def form_invalid(self, form): 
        print("Formulário inválido com erros:", form.errors) 
        messages.error(self.request, 'Erro ao criar evento. Verifique os dados e tente novamente.')
        return self.render_to_response(self.get_context_data(form=form))
    


class EventoDetailView(DetailView):
    model = models.Evento
    template_name = 'evento_detail.html'


@method_decorator(login_required(login_url= 'login'), name = 'dispatch')
class EventoUpdateView(UpdateView):
    model = models.Evento
    template_name = 'evento_update.html'
    form_class = forms.EventoForm
    success_url = reverse_lazy('evento_list')


@method_decorator(login_required(login_url= 'login'), name = 'dispatch')
class EventoDeleteView(DeleteView):
    model = models.Evento
    template_name = 'evento_delete.html'
    success_url = reverse_lazy('evento_list')
