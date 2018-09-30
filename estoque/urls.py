from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('livros/', include([
        path('', views.LivroSearchForm.as_view(), name='livro-list'),
        path('list.json', views.LivroJsonListView.as_view(), name='livro-json-list'),
        path('novo/', views.LivroCreateView.as_view(), name='livro-create'),
        path('<int:pk>/', views.LivroUpdateView.as_view(), name='livro-update'),
    ])),
    path('autores/', include([
        path('', views.AutorListView.as_view(), name='autor-list'),
        path('taken/', views.autor_nome_registrado, name='autor-taken'),
        path('novo/', views.AutorCreateView.as_view(), name='autor-create'),
        path('<int:pk>/', views.AutorUpdateView.as_view(), name='autor-update'),
    ])),
    path('remover/<int:pk>/<str:app>/<str:model>/', views.GenericDeleteView.as_view(), name='generic-delete'),
]
