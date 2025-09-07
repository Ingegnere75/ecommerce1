import string
from core.models import Categoria

def generate_categoria_code():
    from itertools import product

    lettere = string.ascii_uppercase
    codici_possibili = [''.join(p) for p in product(lettere, repeat=3)]
    codici_usati = Categoria.objects.values_list('codice', flat=True)

    for codice in codici_possibili:
        if codice not in codici_usati:
            return codice
