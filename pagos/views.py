from django.shortcuts import render
from .models import Pago

def lista_pagos(request):
    pagos = Pago.objects.all()
    return render(request, 'pagos/lista_pagos.html', {
        'pagos': pagos
    })