from abc import ABC, abstractmethod
from django.contrib import messages
from django.shortcuts import render, get_object_or_404


class FormularioTemplate(ABC):
    """Esqueleto comum das telas de cadastro/edição.

    O fluxo (exibir -> validar -> salvar -> responder) fica fixo em processar();
    as subclasses só trocam os passos que variam.
    """
    form_class = None
    template_name = None
    mensagem_sucesso = ''
    model = None  # usado só nas telas de edição

    # Template method: a ordem dos passos não muda
    def processar(self, request, id=None):
        instancia = self.obter_instancia(id)

        if request.method != 'POST':
            return self.renderizar(request, self.form_class(instance=instancia))

        form = self.form_class(request.POST, instance=instancia)
        if not form.is_valid():
            return self.tratar_invalido(request, form)

        objeto = form.save(commit=False)
        erro = self.antes_de_salvar(request, objeto, form)
        if erro:
            return erro

        objeto.save()
        messages.success(request, self.mensagem_sucesso)
        return self.resposta_sucesso(request)

    # Hooks: têm comportamento padrão, sobrescreve quem precisar
    def obter_instancia(self, id):
        return get_object_or_404(self.model, id=id) if id else None

    def antes_de_salvar(self, request, objeto, form):
        return None  # None = pode salvar; uma resposta interrompe o fluxo

    def tratar_invalido(self, request, form):
        return self.renderizar(request, form)

    def renderizar(self, request, form, status=200):
        return render(request, self.template_name, {'form': form}, status=status)

    # Passo obrigatório
    @abstractmethod
    def resposta_sucesso(self, request):
        ...


class ListagemTemplate(ABC):
    """Esqueleto comum das telas de listagem com campo de busca (?busca=)."""
    template_name = None
    nome_contexto = None
    nome_busca = 'termo_busca'

    # Template method
    def listar(self, request):
        termo = request.GET.get('busca', '')
        queryset = self.consulta_base()
        if termo:
            queryset = self.filtrar(queryset, termo)
        return render(request, self.template_name, {
            self.nome_contexto: queryset,
            self.nome_busca: termo,
        })

    @abstractmethod
    def consulta_base(self):
        ...

    @abstractmethod
    def filtrar(self, queryset, termo):
        ...
