from datetime import date, timedelta

import pytest
from django.urls import reverse

from .models import Colaborador, EPI, Registrar
from .template_methods import FormularioTemplate, ListagemTemplate

pytestmark = pytest.mark.django_db


@pytest.fixture
def colaborador():
    return Colaborador.objects.create(
        nome='Ana Souza', email='ana@exemplo.com', cargo='Soldadora', telefone='11999990000'
    )


@pytest.fixture
def epi():
    return EPI.objects.create(
        nomeEPI='Luva', descricao='Luva de raspa', validade=date(2030, 1, 1),
        quantidade_disponivel=2, codigo='LV-01'
    )


def dados_registro(epi, colaborador, **extra):
    hoje = date.today()
    dados = {
        'equipamento': epi.id,
        'colaborador': colaborador.id,
        'status': 'emprestado',
        'condicao_equipamento': 'bom',
        'data_emprestimo': hoje.isoformat(),
        'data_prevista_da_devolucao': (hoje + timedelta(days=5)).isoformat(),
    }
    dados.update(extra)
    return dados


def test_classes_abstratas_nao_instanciam():
    with pytest.raises(TypeError):
        FormularioTemplate()
    with pytest.raises(TypeError):
        ListagemTemplate()


@pytest.mark.parametrize('nome', [
    'cadastrar_colaborador', 'cadastrar_epi', 'registrar',
    'listar_colaboradores', 'listar_epi', 'listar_registro_relatorio', 'relatorio_colaborador',
])
def test_get_exibe_pagina(client, nome):
    assert client.get(reverse(nome)).status_code == 200


# ---------- Cadastro de colaborador ----------

def test_cadastro_colaborador_valido_redireciona(client):
    resposta = client.post(reverse('cadastrar_colaborador'), {
        'nome': 'Bruno', 'email': 'bruno@exemplo.com', 'cargo': 'Serralheiro', 'telefone': '1188887777'
    })
    assert resposta.status_code == 302
    assert resposta.url == reverse('cadastrar_colaborador')
    assert Colaborador.objects.filter(nome='Bruno').exists()


def test_cadastro_colaborador_invalido_retorna_400_html(client):
    resposta = client.post(reverse('cadastrar_colaborador'), {'nome': ''})
    assert resposta.status_code == 400
    assert 'form' in resposta.context
    assert Colaborador.objects.count() == 0


def test_cadastro_colaborador_invalido_retorna_400_json(client):
    resposta = client.post(reverse('cadastrar_colaborador'), {'nome': ''},
                           HTTP_ACCEPT='application/json')
    assert resposta.status_code == 400
    assert 'nome' in resposta.json()['campos']


# ---------- Cadastro de EPI ----------

def test_cadastro_epi_valido_devolve_form_vazio(client):
    resposta = client.post(reverse('cadastrar_epi'), {
        'nomeEPI': 'Capacete', 'descricao': 'Capacete classe B', 'validade': '2030-01-01',
        'quantidade_disponivel': 5, 'codigo': 'CP-01'
    })
    assert resposta.status_code == 200
    assert not resposta.context['form'].is_bound
    assert EPI.objects.filter(nomeEPI='Capacete').exists()


def test_cadastro_epi_invalido_nao_salva(client):
    resposta = client.post(reverse('cadastrar_epi'), {'nomeEPI': 'Capacete'})
    assert resposta.status_code == 200
    assert resposta.context['form'].errors
    assert EPI.objects.count() == 0


# ---------- Registro (hook antes_de_salvar com baixa de estoque) ----------

def test_registro_emprestimo_baixa_estoque(client, epi, colaborador):
    resposta = client.post(reverse('registrar'), dados_registro(epi, colaborador))
    assert resposta.status_code == 302
    assert resposta.url == reverse('registrar')
    epi.refresh_from_db()
    assert epi.quantidade_disponivel == 1
    assert Registrar.objects.count() == 1


def test_registro_sem_estoque_nao_salva(client, epi, colaborador):
    epi.quantidade_disponivel = 0
    epi.save()
    resposta = client.post(reverse('registrar'), dados_registro(epi, colaborador))
    assert resposta.status_code == 200
    assert Registrar.objects.count() == 0
    mensagens = [str(m) for m in resposta.context['messages']]
    assert 'Não há mais itens disponíveis para este EPI!' in mensagens


def test_registro_devolvido_nao_mexe_no_estoque(client, epi, colaborador):
    dados = dados_registro(epi, colaborador, status='devolvido', observacao='ok',
                           data_devolucao=date.today().isoformat())
    client.post(reverse('registrar'), dados)
    epi.refresh_from_db()
    assert epi.quantidade_disponivel == 2
    assert Registrar.objects.count() == 1


def test_registro_invalido_mostra_erro(client):
    resposta = client.post(reverse('registrar'), {})
    assert resposta.status_code == 200
    mensagens = [str(m) for m in resposta.context['messages']]
    assert 'Item não foi cadastrado. Verifique os campos obrigatórios.' in mensagens


# ---------- Edições (hook obter_instancia) ----------

def test_edicao_colaborador_atualiza(client, colaborador):
    url = reverse('editar_colaborador', args=[colaborador.id])
    assert client.get(url).context['form'].instance == colaborador
    resposta = client.post(url, {
        'nome': 'Ana Lima', 'email': 'ana@exemplo.com', 'cargo': 'Soldadora', 'telefone': '11999990000'
    })
    assert resposta.url == reverse('listar_colaboradores')
    colaborador.refresh_from_db()
    assert colaborador.nome == 'Ana Lima'
    assert Colaborador.objects.count() == 1


def test_edicao_epi_atualiza(client, epi):
    resposta = client.post(reverse('editar_epi', args=[epi.id]), {
        'nomeEPI': 'Luva nitrílica', 'descricao': 'Luva', 'validade': '2030-01-01',
        'quantidade_disponivel': 9, 'codigo': 'LV-01'
    })
    assert resposta.url == reverse('listar_epi')
    epi.refresh_from_db()
    assert epi.quantidade_disponivel == 9


def test_edicao_inexistente_retorna_404(client):
    assert client.get(reverse('editar_colaborador', args=[999])).status_code == 404
    assert client.get(reverse('editar_epi', args=[999])).status_code == 404


# ---------- Listagens ----------

def test_lista_colaboradores_filtra_pela_busca(client, colaborador):
    Colaborador.objects.create(nome='Carlos', email='c@exemplo.com', cargo='x', telefone='1')
    resposta = client.get(reverse('listar_colaboradores'), {'busca': 'ana'})
    assert list(resposta.context['colaboradores']) == [colaborador]
    assert resposta.context['termo_busca'] == 'ana'


def test_lista_epi_usa_chave_busca(client, epi):
    resposta = client.get(reverse('listar_epi'), {'busca': 'luv'})
    assert list(resposta.context['equipamentos']) == [epi]
    assert resposta.context['busca'] == 'luv'


def test_relatorio_so_mostra_emprestados(client, epi, colaborador):
    base = dict(equipamento=epi, colaborador=colaborador, condicao_equipamento='bom',
                data_emprestimo=date.today(), data_prevista_da_devolucao=date.today())
    emprestado = Registrar.objects.create(status='emprestado', **base)
    Registrar.objects.create(status='devolvido', **base)

    relatorio = client.get(reverse('relatorio_colaborador'))
    assert list(relatorio.context['registros']) == [emprestado]

    todos = client.get(reverse('listar_registro_relatorio'), {'busca': 'ana'})
    assert todos.context['registros'].count() == 2
