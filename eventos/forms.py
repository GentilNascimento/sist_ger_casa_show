from django import forms
from .models import Evento
from artistas.models import Artista

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['artista', 'horario', 'descricao', 'scheduled_date']
        widgets = {
            'artista': forms.Select(attrs={'class': 'form-control'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'min': '1000-01-01', 'max': '9999-12-31'}),
        }
        labels = {
            'horario': 'Horário do Evento',
            'descricao': 'Descrição',
            'scheduled_date': 'Data Agendada',
        }