from django import forms
from .models import Evento
from artistas.models import Artista

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['artista', 'data', 'horario', 'descricao', 'scheduled_date', 'send_date']
        widgets = {
            'artista': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'send_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels ={
            'data': 'Data do Evento',
            'horario': 'Horário do Evento',
            'descricao': 'Descrição',
            'scheduled_date': 'Data Agendada',
            'send_date': 'Data de Envio',           
        }
        
        
        
        
        
        
        
                     