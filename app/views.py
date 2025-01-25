from django.shortcuts import render

def anotacoes_view(request):
    return render(request, 'anotacoes.html')