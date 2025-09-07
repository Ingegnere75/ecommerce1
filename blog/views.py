from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from .models import ArticoloBlog, CommentoBlog, ProdottoSuggerito
import re

# 🏠 HOME BLOG
def blog_home(request):
    articoli = ArticoloBlog.objects.order_by('-data_pubblicazione')
    prodotti = ProdottoSuggerito.objects.order_by('-data_pubblicazione')
    return render(request, 'blog/home.html', {
        'articoli': articoli,
        'prodotti': prodotti,
    })


# 🔍 DETTAGLIO ARTICOLO
def blog_detail(request, slug):
    articolo = get_object_or_404(ArticoloBlog, slug=slug)
    commenti = CommentoBlog.objects.filter(post=articolo, risposta_a__isnull=True).order_by('-data_pubblicazione')

    prodotti_collegati = list(articolo.prodotti_correlati.all())

    # 🔗 Sostituzione dei titoli dei prodotti nel contenuto con link HTML
    contenuto = articolo.contenuto
    for prodotto in ProdottoSuggerito.objects.all():
        if prodotto.titolo in contenuto:
            if prodotto not in prodotti_collegati:
                prodotti_collegati.append(prodotto)
            pattern = r'\b(' + re.escape(prodotto.titolo) + r')\b'
            link = f"<a href='/prodotti-correlati/{prodotto.id}/' class='text-decoration-underline text-primary fw-semibold'>\\1</a>"
            contenuto = re.sub(pattern, link, contenuto, count=1)

    # 📝 Inserimento commento
    if request.method == 'POST':
        if request.user.is_authenticated:
            testo = request.POST.get('testo', '').strip()
            emoji = request.POST.get('emoji', '👍')
            if testo:
                CommentoBlog.objects.create(
                    post=articolo,
                    utente=request.user,
                    testo=testo,
                    emoji=emoji
                )
            return redirect('blog-detail', slug=slug)
        else:
            return redirect('login')

    return render(request, 'blog/detail.html', {
        'articolo': articolo,
        'commenti': commenti,
        'immagine_sfondo': articolo.immagine_sfondo.url if articolo.immagine_sfondo else None,
        'video': articolo.video.url if articolo.video else None,
        'contorno_card': articolo.contorno_card,
        'contenuto_con_link': mark_safe(contenuto),
        'prodotti_linkati': prodotti_collegati[:5],  # massimo 5 in base alla larghezza layout
    })


from django.shortcuts import render
from .models import BannerInformativo

def banner_blog(request):
    banner = BannerInformativo.objects.filter(visibile=True).order_by('-data_creazione').first()
    return render(request, 'blog/banner.html', {'banner': banner})
from django.shortcuts import render

# Create your views here.
