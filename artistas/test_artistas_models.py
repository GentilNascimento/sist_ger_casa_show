import pytest
from artistas.models import Artista, Message
from django.core.exceptions import ValidationError
from datetime import datetime

@pytest.mark.django_db
def test_send_date_year_validation():
    artista = Artista.objects.create(
        nome="Teste Artista",
        cpf="12345678901",
        telefone="1234567890",
        banco="Banco Teste",
        tipo_chave_pix="cel",
        chave_pix="12345",
        email="teste@artista.com"
    )
    
    #Tenta criar uma msg com ano inválido
    invalid_date = datetime(202400, 1, 1, 12, 0) #ano com 6 dígitos
    message = Message(artista=artista, conteudo="Teste mensagem", send_date=invalid_date)
    
    with pytest.raises(ValidationError) as excinfo:
        message.full_clean() #valida o modelo

    assert "O ano deve ter exatamente 4 dígitos" in str(excinfo.value)
    