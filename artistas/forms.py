from django import forms
from validate_docbr import CPF
from . import models
from .models import Artista, Message

class ArtistaForm(forms.ModelForm):
    class Meta:
        model = models.Artista
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_chave_pix': forms.Select(attrs={'class': 'form-control'}),
            'chave_pix': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),            
        }
        
    
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf_validator = CPF()
        if not cpf_validator.validate(cpf):
            raise forms.ValidationError('CPF inválido.')
        return cpf

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['conteudo', 'send_date']
        widgets = {
            'send_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control',}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control'}),
        }