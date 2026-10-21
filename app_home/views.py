from django.shortcuts import render, redirect, get_object_or_404
from .forms import ColaboradorForm
from .forms import EPIForm
from .forms import RegistrarForm
from django.contrib import messages
from .models import Colaborador
from .models import EPI
from .models import Registrar
from .models import Aviso
from .template_methods import FormularioTemplate, ListagemTemplate
from datetime import date, timedelta
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

STATUS_QUE_RETIRAM = ['emprestado', 'em_uso', 'fornecido', 'danificado', 'perdido']


# ---------- Formulários (Template Method: FormularioTemplate.processar) ----------

class CadastroColaborador(FormularioTemplate):
    form_class = ColaboradorForm
    template_name = 'app_home/pages/cadastrar_colaborador.html'
    mensagem_sucesso = 'Colaborador cadastrado com sucesso!'

    def tratar_invalido(self, request, form):
        # Formulário inválido: quem pedir JSON (ex.: Postman com o header
        # "Accept: application/json") recebe o response de erro em JSON.
        if 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'dados invalidos': 'dados incorreto ou invalidos',
                'campos': form.errors.get_json_data()
            }, status=400)

        # Navegador: devolve a página de cadastro com os erros de cada campo
        # (o template exibe field.errors abaixo de cada input).
        return self.renderizar(request, form, status=400)

    def resposta_sucesso(self, request):
        return redirect('cadastrar_colaborador')


class CadastroEPI(FormularioTemplate):
    form_class = EPIForm
    template_name = 'app_home/pages/cadastrar_epi.html'
    mensagem_sucesso = 'EPI cadastrado com sucesso!'

    def resposta_sucesso(self, request):
        return self.renderizar(request, EPIForm())


class RegistroEPI(FormularioTemplate):
    form_class = RegistrarForm
    template_name = 'app_home/pages/registrar.html'
    mensagem_sucesso = 'Registrado com sucesso!'

    def antes_de_salvar(self, request, registro, form):
        if registro.status in STATUS_QUE_RETIRAM:
            if registro.equipamento.quantidade_disponivel <= 0:
                messages.error(request, "Não há mais itens disponíveis para este EPI!")
                return self.renderizar(request, form)

            registro.equipamento.quantidade_disponivel -= 1
            registro.equipamento.save()
        return None

    def tratar_invalido(self, request, form):
        messages.error(request, "Item não foi cadastrado. Verifique os campos obrigatórios.")
        return super().tratar_invalido(request, form)

    def resposta_sucesso(self, request):
        return redirect('registrar')


class EdicaoColaborador(FormularioTemplate):
    model = Colaborador
    form_class = ColaboradorForm
    template_name = 'app_home/pages/editar_colaborador.html'
    mensagem_sucesso = 'Colaborador atualizado!'

    def resposta_sucesso(self, request):
        return redirect('listar_colaboradores')


class EdicaoEPI(FormularioTemplate):
    model = EPI
    form_class = EPIForm
    template_name = 'app_home/pages/editar_epi.html'
    mensagem_sucesso = 'Equipamento atualizado!'

    def resposta_sucesso(self, request):
        return redirect('listar_epi')


# ---------- Listagens (Template Method: ListagemTemplate.listar) ----------

class ListaColaboradores(ListagemTemplate):
    template_name = 'app_home/pages/listar_colaboradores.html'
    nome_contexto = 'colaboradores'

    def consulta_base(self):
        return Colaborador.objects.all()

    def filtrar(self, queryset, termo):
        return queryset.filter(nome__icontains=termo)


class ListaEPI(ListagemTemplate):
    template_name = 'app_home/pages/listar_epi.html'
    nome_contexto = 'equipamentos'
    nome_busca = 'busca'

    def consulta_base(self):
        return EPI.objects.all()

    def filtrar(self, queryset, termo):
        return queryset.filter(nomeEPI__icontains=termo)


class ListaRegistros(ListagemTemplate):
    template_name = 'app_home/pages/listar_registro_relatorio.html'
    nome_contexto = 'registros'

    def consulta_base(self):
        return Registrar.objects.all()

    def filtrar(self, queryset, termo):
        return queryset.filter(colaborador__nome__icontains=termo)


class RelatorioColaborador(ListaRegistros):
    template_name = 'app_home/pages/relatorio_colaborador.html'

    def consulta_base(self):
        return Registrar.objects.filter(status='emprestado')


# Mesmos nomes de antes, então o urls.py não muda
cadastrar_colaborador = CadastroColaborador().processar
cadastrar_epi = CadastroEPI().processar
registrar = RegistroEPI().processar
editar_colaborador = EdicaoColaborador().processar
editar_epi = EdicaoEPI().processar
listar_colaboradores = ListaColaboradores().listar
listar_epi = ListaEPI().listar
listar_registro_relatorio = ListaRegistros().listar
relatorio_colaborador = RelatorioColaborador().listar


# ---------- Views com lógica própria ----------

def editar_status(request, id):
    registro = get_object_or_404(Registrar, id=id)
    epi = registro.equipamento

    if request.method == 'POST':
        status_anterior = registro.status
        status_atualizado = request.POST.get('status')

        registro.status = status_atualizado
        registro.save()

        if status_anterior != 'devolvido' and status_atualizado == 'devolvido':
            epi.quantidade_disponivel += 1
            epi.save()

        elif status_anterior == 'devolvido' and status_atualizado in STATUS_QUE_RETIRAM:
            if epi.quantidade_disponivel > 0:
                epi.quantidade_disponivel -= 1
                epi.save()

        messages.success(request, 'Status atualizado com sucesso!')

        return redirect('relatorio_colaborador')
    else:
        form = RegistrarForm(instance=registro)

    return render(request, 'app_home/pages/editar_status.html', {
        'form': form,
        'registro': registro
    })


def excluir_epi(request, id):
    epi = get_object_or_404(EPI, id=id)
    epi.delete()
    messages.success(request, 'EPI excluído com sucesso!')
    return redirect('listar_epi')

def cadastro_epi_sucesso(request):
    return render(request,'app_home/pages/cadastro_epi_sucesso.html')

def excluir_colaborador(request, id):
    colaborador = get_object_or_404(Colaborador, id=id)
    colaborador.delete()
    messages.success(request, 'Colaborador excluído com sucesso!')
    return redirect('listar_colaboradores')

def sucesso(request):
    return render(request,'app_home/pages/sucesso.html')

def registro_sucesso(request):
    return render(request,'app_home/pages/registro_sucesso.html')

def perfil(request):
    return render(request, 'app_home/pages/perfil.html')

def visualizar_quantidade_epi(request):

    epi_data = EPI.objects.all()

    epi_data_serialized = []
    for epi in epi_data:
        status_counts = {
            'emprestado': epi.registros.filter(status='emprestado').count(),
            'em_uso': epi.registros.filter(status='em_uso').count(),
            'fornecido': epi.registros.filter(status='fornecido').count(),
            'devolvido': epi.registros.filter(status='devolvido').count(),
            'danificado': epi.registros.filter(status='danificado').count(),
            'perdido': epi.registros.filter(status='perdido').count(),
        }
        epi_data_serialized.append({
            'nomeEPI': epi.nomeEPI,
            'quantidade_disponivel': epi.quantidade_disponivel,
            'descricao': epi.descricao,
            'status_counts': status_counts,
        })

    return render(request, 'app_home/pages/visualizar_quantidade_epi.html', {'epi_data': epi_data_serialized})

def avisos(request):
    total_epis = EPI.objects.count()
    total_colaboradores = Colaborador.objects.count()

    epis_a_devolver = Registrar.objects.filter(
        status__in=['emprestado', 'em_uso'],
        data_devolucao__isnull=True
    ).count()

    avisos = Aviso.objects.all()

    hoje = date.today()
    amanha = hoje + timedelta(days=1)

    registros_para_avisar = Registrar.objects.filter(
        status__in=['emprestado', 'em_uso'],
        data_prevista_da_devolucao__in=[hoje, amanha]
    )

    avisos_automaticos = []

    for registro in registros_para_avisar:
        titulo = "Devolução de EPI Pendente"
        mensagem = f"O EPI '{registro.equipamento.nomeEPI}' emprestado para '{registro.colaborador.nome}' deve ser devolvido em {registro.data_prevista_da_devolucao.strftime('%d/%m/%Y')}."
        avisos_automaticos.append({
            'titulo': titulo,
            'mensagem': mensagem,
            'data_criacao': registro.data_prevista_da_devolucao
        })

    context = {
        'total_epis': total_epis,
        'total_colaboradores': total_colaboradores,
        'epis_a_devolver': epis_a_devolver,
        'avisos': list(avisos) + avisos_automaticos,
    }

    return render(request, 'app_home/pages/avisos.html', context)

@login_required
def home(request):
    return render(request, 'app_home/pages/home.html')

def home_view(request):
    return render(request, 'app_home/pages/home.html')

def resposta(sucesso, codigo, mensagem, status, dados=None, erros=None):
    corpo = {
        "sucesso": sucesso,
        "codigo": codigo,
        "mensagem": mensagem,
    }
    if dados is not None:
        corpo["dados"] = dados
    if erros is not None:
        corpo["erros"] = erros
    return JsonResponse(
        corpo,
        status=status,
        json_dumps_params={"ensure_ascii": False},  # mantém os acentos
    )


@csrf_exempt
@require_http_methods(["POST"])
def teste_erro_400(request):
    return JsonResponse({
        "sucesso": False,
        "codigo": "DADOS_INVALIDOS",
        "mensagem": "Os dados enviados são inválidos.",
    }, status=400, json_dumps_params={"ensure_ascii": False})
