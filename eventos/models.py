from django.db import models
from artistas.models import Artista


class Evento(models.Model):

    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    data = models.DateField()
    horario = models.TimeField()
    descricao = models.TextField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    send_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['data']


    def __str__(self):
        return f"{self.artista.nome} - {self.formatted_data()} {self.formatted_horario()}"

    def formatted_data(self):
        return self.data.strftime('%d-%m-%Y')

    def formatted_horario(self):
        return self.horario.strftime('%H-%M')
