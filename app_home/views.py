from django.shortcuts import render, redirect, get_object_or_404
from .forms import ColaboradorForm
from .forms import EPIForm
from .forms import RegistrarForm
from django.contrib import messages
from .models import Colaborador
from .models import EPI
from .models import Registrar
from .models import Aviso
from datetime import date, timedelta
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def home(request):
    return render(request, 'app_home/pages/home.html')

def listar_colaboradores(request): 
    termo_busca = request.GET.get('busca', '')  # pega o valor do campo de busca da URL
    if termo_busca:
        colaboradores = Colaborador.objects.filter(nome__icontains=termo_busca)
    else:
        colaboradores = Colaborador.objects.all()
        
    return render(request, 'app_home/pages/listar_colaboradores.html', {
        'colaboradores': colaboradores,
        'termo_busca': termo_busca,
    })

def listar_epi(request):
    busca = request.GET.get('busca', '')
    if busca:
        epi = EPI.objects.filter(nomeEPI__icontains=busca)
    else:      
        epi = EPI.objects.all()
        
    return render(request, 'app_home/pages/listar_epi.html', {'equipamentos': epi, 'busca': busca})


def editar_colaborador(request, id):
    colaborador = get_object_or_404(Colaborador, id=id)
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colaborador atualizado!')
            return redirect('listar_colaboradores')
    else:
        form = ColaboradorForm(instance=colaborador)    
    return render(request, 'app_home/pages/editar_colaborador.html', {'form': form})

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

        elif status_anterior == 'devolvido' and status_atualizado in ['emprestado', 'em_uso', 'fornecido', 'danificado', 'perdido']:
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

def editar_epi(request, id):
    epi = get_object_or_404(EPI, id=id)
    if request.method == 'POST':
        form = EPIForm(request.POST, instance=epi)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipamento atualizado!')
            return redirect('listar_epi')
    else:
        form = EPIForm(instance=epi)

    return render(request, 'app_home/pages/editar_epi.html', {'form': form})

def excluir_colaborador(request, id):
    colaborador = get_object_or_404(Colaborador, id=id)
    colaborador.delete()
    messages.success(request, 'Colaborador excluído com sucesso!')
    return redirect('listar_colaboradores')

def cadastrar_colaborador(request):
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colaborador cadastrado com sucesso!')
            return redirect(cadastrar_colaborador)
    else:
        form = ColaboradorForm()
    return render(request, 'app_home/pages/cadastrar_colaborador.html', {'form' : form})

def sucesso(request):
    return render(request,'app_home/pages/sucesso.html')

def cadastrar_epi(request):
    if request.method == 'POST':
        form = EPIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'EPI cadastrado com sucesso!')
            form = EPIForm()  
    else:
        form = EPIForm()
    
    return render(request, 'app_home/pages/cadastrar_epi.html', {'form': form})


def registrar(request):
    if request.method == 'POST':
        form = RegistrarForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)  
            
            if registro.status in ['emprestado', 'em_uso', 'fornecido', 'danificado', 'perdido']:
                if registro.equipamento.quantidade_disponivel <= 0:
                    messages.error(request, "Não há mais itens disponíveis para este EPI!")
                    return render(request, 'app_home/pages/registrar.html', {'form': form})

                registro.equipamento.quantidade_disponivel -= 1
                registro.equipamento.save()

            registro.save()  
            messages.success(request, 'Registrado com sucesso!')  
            return redirect(registrar)       
        else:        
            messages.error(request, "Item não foi cadastrado. Verifique os campos obrigatórios.")
    else:
        form = RegistrarForm()

    return render(request, 'app_home/pages/registrar.html', {'form': form})


def registro_sucesso(request):
    return render(request,'app_home/pages/registro_sucesso.html')

def listar_registro_relatorio(request):
    termo_busca = request.GET.get('busca', '')

    if termo_busca:
        registros = Registrar.objects.filter(
           colaborador__nome__icontains=termo_busca
        )
    else:
        registros = Registrar.objects.all()

    return render(request, 'app_home/pages/listar_registro_relatorio.html', {
        'registros': registros,
        'termo_busca': termo_busca,
    })


def relatorio_colaborador(request):
    termo_busca = request.GET.get('busca', '')
    
    if termo_busca:
        registros = Registrar.objects.filter(
            status='emprestado',
            colaborador__nome__icontains=termo_busca
        )
    else:
        registros = Registrar.objects.filter(status='emprestado')
        
    return render(request, 'app_home/pages/relatorio_colaborador.html', {
        'registros': registros,
        'termo_busca': termo_busca,
    })

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
