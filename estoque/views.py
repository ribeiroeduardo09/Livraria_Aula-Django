from django.apps import apps
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.edit import FormMixin
from django.views.generic.edit import ModelFormMixin

from estoque.models import Autor, Livro, Editora, Loja
from estoque.forms import LivroForm, LivroSearchForm


def index(request):
    livro_mais_barato = Livro.objects.order_by('-preco').last()
    livro_mais_caro = Livro.objects.order_by('-preco').first()
    livro_preco_medio = Livro.objects.filter().aggregate(Avg('preco')) or 0
    qtd_autores = Autor.objects.count()
    qtd_editoras = Editora.objects.count()
    qtd_livros = Livro.objects.count()
    qtd_lojas = Loja.objects.count()
    return render(request, 'estoque/index.html', {
        'livro_mais_barato': livro_mais_barato,
        'livro_mais_caro': livro_mais_caro,
        'livro_preco_medio': livro_preco_medio.get('preco__avg', 0),
        'qtd_autores': qtd_autores,
        'qtd_editoras': qtd_editoras,
        'qtd_livros': qtd_livros,
        'qtd_lojas': qtd_lojas,
        'page_info': 'Início',
    })


def autor_nome_registrado(request):
    nome = request.GET.get('nome', None)
    data = {
        'is_taken': Autor.objects.filter(nome__iexact=nome).exists(),
        'message': 'Válido'
    }
    if data['is_taken']:
        data['message'] = 'O Autor já está cadastrado'
    return JsonResponse(data)


class JsonListMixin(object):
    json_fields = []

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset().values_list(*self.json_fields)
        json_dict = {
            'header': self.json_fields,
            'object_list': list(self.object_list)
        }
        return JsonResponse(json_dict)


class PageInfoMixin(object):
    page_info = None

    def get_page_info(self):
        if self.model:
            return {
                'page_info': self.model._meta.verbose_name,
                'page_info_plural': self.model._meta.verbose_name_plural,
            }
        return None

    def get_context_data(self, **kwargs):
        if self.page_info is None:
            kwargs.update(self.get_page_info())
        return super().get_context_data(**kwargs)


class AutorListView(PageInfoMixin, ModelFormMixin, ListView):
    model = Autor
    fields = '__all__'

    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)


class AutorCreateView(PageInfoMixin, CreateView):
    model = Autor
    fields = '__all__'
    success_url = reverse_lazy('autor-list')

    def form_valid(self, form):
        if self.request.is_ajax():
            obj = form.save()
            return JsonResponse({
                'obj': {
                    'nome': obj.nome,
                    'idade': obj.idade,
                }
            })
        else:
            return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({
                'errors': form.errors,
                'non_field_errors': form.non_field_errors()
            })
        else:
            return super().form_invalid(form)


class AutorUpdateView(PageInfoMixin, UpdateView):
    model = Autor
    fields = '__all__'
    success_url = reverse_lazy('autor-list')


class GenericDeleteView(DeleteView):
    model = None
    template_name = 'estoque/confirm_delete.html'

    def get_object(self):
        ModelClass = apps.get_model(
            app_label=self.kwargs['app'],
            model_name=self.kwargs['model']
        )
        obj = get_object_or_404(ModelClass, pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        return self.request.GET.get('success_url', '/')


class LivroListView(PageInfoMixin, ListView):
    model = Livro


class LivroCreateView(PageInfoMixin, CreateView):
    model = Livro
    form_class = LivroForm
    success_url = reverse_lazy('livro-list')


class LivroUpdateView(PageInfoMixin, UpdateView):
    model = Livro
    fields = '__all__'
    success_url = reverse_lazy('livro-list')


class SearchFormListView(FormMixin, ListView):
    def get(self, request, *args, **kwargs):
        self.form = self.get_form(self.get_form_class())
        self.object_list = self.form.get_queryset()
        return self.render_to_response(self.get_context_data(object_list=self.object_list, form=self.form))

    def get_form_kwargs(self):
        return {'initial': self.get_initial(), 'data': self.request.GET}


class LivroSearchForm(PageInfoMixin, SearchFormListView):
    model = Livro
    form_class = LivroSearchForm


class LivroJsonListView(JsonListMixin, LivroListView):
    json_fields = [
        'nome',
        'paginas',
        'preco',
        'avaliacao',
        'editora__nome',
        'autores__nome',
    ]
