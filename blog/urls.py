from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_home, name='blog-home'),  # Home del blog
    path('<slug:slug>/', views.blog_detail, name='blog-detail'),  # Dettaglio articolo 
    path('banner/', views.banner_blog, name='banner-blog'),
    
]
