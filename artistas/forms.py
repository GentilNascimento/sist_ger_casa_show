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
    send_date = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M:%S'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    class Meta:
        model = Message
        fields = ['conteudo', 'send_date']
        widgets = {
            'conteudo': forms.Textarea(attrs={'class': 'form-control'}),
        }
        
    def clean_send_date(self):
        send_date = self.cleaned_data.get('send_date')
        if send_date.year < 1000 or send_date.year > 9999:
            raise forms.ValidationError('O ano deve ter exatamente 4 dígitos.')
        return send_date