# Sistema de Monitoramento e Distribuição de EPIs

Aplicação web em **Django** para controlar o cadastro, a distribuição e a devolução de Equipamentos de Proteção Individual (EPIs) dos colaboradores da **Vanderson Serralheria**.

| | |
|---|---|
| **Empresa** | Vanderson Serralheria — CNPJ 34.576.981/0001-31 |
| **Participante** | Vitória Beatriz Silva de Carvalho |
| **Status** | Protótipo funcional |

---

## Objetivo

Garantir que todos os trabalhadores recebam, utilizem e mantenham adequadamente os EPIs necessários para sua segurança. O sistema centraliza:

- o cadastro de colaboradores e de equipamentos (com validade e estoque);
- o registro de cada entrega, empréstimo e devolução;
- o acompanhamento do estado de conservação de cada item;
- avisos de devoluções próximas do prazo.

Com isso, a empresa reduz o risco de acidentes, mantém o histórico exigido pelas normas regulamentadoras (em especial a **NR-6**) e promove um ambiente de trabalho mais seguro.

---

## Funcionalidades

- **Autenticação** — login e logout com o sistema de usuários do Django.
- **Colaboradores** — cadastrar, listar (com busca), editar e excluir.
- **EPIs** — cadastrar, listar (com busca), editar e excluir; controle de validade, código e quantidade disponível.
- **Registro de movimentação** — vincula um EPI a um colaborador, com status, condição do equipamento, data de empréstimo e devolução prevista.
- **Controle automático de estoque**
  - status que retiram o item do estoque (`emprestado`, `em_uso`, `fornecido`, `danificado`, `perdido`) baixam 1 unidade;
  - o registro é bloqueado quando não há unidades disponíveis;
  - ao mudar o status para `devolvido`, a unidade volta ao estoque.
- **Relatórios** — listagem geral de registros e relatório por colaborador.
- **Painel de quantidades** — para cada EPI, o estoque atual e a contagem de registros por status.
- **Avisos** — avisos manuais (cadastrados no admin) e avisos automáticos para devoluções previstas para hoje ou amanhã.
- **Resposta JSON para APIs** — o cadastro de colaborador devolve `400` em JSON quando a requisição envia `Accept: application/json` (usado nos testes com Postman).

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3 |
| Framework | Django 6.1 |
| Banco de dados | SQLite (desenvolvimento) |
| Front-end | Templates Django, HTML, CSS e JavaScript |
| Testes | pytest + pytest-django; Postman para testes de API |

---

## Estrutura do projeto

```
vanderson_serralheria/
├── equipamentos_epi/          # Configuração do projeto Django
│   ├── settings.py
│   └── urls.py
├── app_home/                  # Aplicação principal
│   ├── models.py              # Colaborador, EPI, Registrar, Aviso
│   ├── forms.py               # ModelForms das telas de cadastro
│   ├── template_methods.py    # Classes-base (padrão Template Method)
│   ├── views.py               # Views das telas
│   ├── urls.py                # Rotas da aplicação
│   ├── templates/             # Páginas HTML
│   ├── static/                # CSS e JavaScript
│   ├── migrations/
│   ├── tests.py
│   └── test_template_methods.py
├── text/mysql.txt             # Modelagem inicial do banco (referência)
├── pytest.ini
└── manage.py
```

---

## Modelo de dados

| Modelo | Campos principais |
|---|---|
| **Colaborador** | `nome`, `email`, `cargo`, `telefone` |
| **EPI** | `nomeEPI`, `descricao`, `validade`, `quantidade_disponivel`, `codigo` |
| **Registrar** | `equipamento` (FK → EPI), `colaborador` (FK → Colaborador), `status`, `condicao_equipamento`, `observacao`, `data_emprestimo`, `data_prevista_da_devolucao`, `data_devolucao` |
| **Aviso** | `titulo`, `mensagem`, `data_criacao` |

**Status do registro:** Emprestado, Em uso, Fornecido, Devolvido, Danificado, Perdido.

**Condição do equipamento:** Bom estado, Usado, Em manutenção, Quebrado/Danificado, Indisponível, Vencido, Aguardando substituição, Contaminado, Em descartabilidade.

---

## Arquitetura: padrão Template Method

As telas de formulário e de listagem seguem o padrão de projeto **Template Method**, definido em `app_home/template_methods.py`.

**`FormularioTemplate`** fixa o fluxo de cadastro e edição:

```
processar()
  ├─ obter_instancia()      # hook: busca o objeto na edição (404 se não existir)
  ├─ GET  → renderizar()
  └─ POST → validar o form
             ├─ inválido → tratar_invalido()   # hook
             └─ válido   → antes_de_salvar()   # hook (ex.: baixa de estoque)
                          → salvar → mensagem de sucesso
                          → resposta_sucesso() # obrigatório nas subclasses
```

**`ListagemTemplate`** fixa o fluxo das listagens com busca (`?busca=`): as subclasses implementam apenas `consulta_base()` e `filtrar()`.

Implementações concretas em `views.py`: `CadastroColaborador`, `CadastroEPI`, `RegistroEPI`, `EdicaoColaborador`, `EdicaoEPI`, `ListaColaboradores`, `ListaEPI`, `ListaRegistros` e `RelatorioColaborador`.

O ganho é eliminar a lógica repetida entre as telas: cada view só declara o que muda (formulário, template, mensagem e destino), e regras específicas, como a baixa de estoque, ficam isoladas em um único hook.

---

## Como executar

### Pré-requisitos

- Python 3.12 ou superior
- pip

### Instalação

```bash
git clone <url-do-repositorio>
cd vanderson_serralheria
```

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows
.venv\Scripts\activate
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instale as dependências, aplique as migrações e crie um usuário para o login:

```bash
pip install django pytest pytest-django
```

```bash
python manage.py migrate
```

```bash
python manage.py createsuperuser
```

```bash
python manage.py runserver
```

Acesse **http://127.0.0.1:8000/** e entre com o usuário criado. O painel administrativo fica em **/admin/**.

---

## Rotas principais

| Rota | Descrição |
|---|---|
| `/` | Login |
| `/home/` | Página inicial |
| `/cadastrar_colaborador/` | Cadastro de colaborador |
| `/listar_colaboradores/` | Lista de colaboradores (busca, edição e exclusão) |
| `/cadastrar_epi/` | Cadastro de EPI |
| `/listar_epi/` | Lista de EPIs (busca, edição e exclusão) |
| `/registrar/` | Registro de entrega/empréstimo de EPI |
| `/listar_registro_relatorio/` | Relatório geral de registros |
| `/relatorio_colaborador/` | Relatório por colaborador |
| `/editar_status/<id>/` | Atualização de status (devolve ao estoque quando aplicável) |
| `/visualizar_quantidade_epi/` | Estoque e contagem por status |
| `/avisos/` | Indicadores e avisos de devolução |
| `/logout/` | Encerrar sessão |
| `/admin/` | Administração do Django |

---

## Testes

### Testes automatizados (pytest)

```bash
pytest
```

Os testes em `app_home/test_template_methods.py` cobrem:

- as classes abstratas não podem ser instanciadas;
- cadastro válido e inválido de colaborador (resposta `400` em HTML e em JSON);
- cadastro de EPI e bloqueio de dados inválidos;
- baixa de estoque no registro, bloqueio sem estoque e devolução sem alterar o estoque;
- edição de colaborador e EPI, e `404` para registros inexistentes;
- filtros de busca nas listagens e no relatório.

### Testes de API (Postman)

O endpoint `/cadastrar_colaborador/` aceita requisições `POST` com o header `Accept: application/json`. Com dados inválidos, a resposta é:

```json
{
  "dados invalidos": "dados incorreto ou invalidos",
  "campos": { "email": [{ "message": "Enter a valid email address.", "code": "invalid" }] }
}
```

O parecer técnico e a apresentação dos testes estão na pasta superior do projeto (`Parecer Técnico de Teste – Cadastro de Colaborador` e `Apresentacao_Postman_Parecer_Tecnico`).

---

## Limitações conhecidas e próximos passos

Por se tratar de um protótipo, alguns pontos ainda precisam ser tratados antes de um uso em produção:

- **Segurança**
  - mover `SECRET_KEY` para variável de ambiente e desativar `DEBUG`;
  - exigir login (`@login_required`) em todas as telas, não só na página inicial;
  - fazer as exclusões apenas via `POST`, com confirmação.
- **Dependências** — criar um `requirements.txt` com as versões fixadas.
- **Banco de dados** — migrar do SQLite para MySQL/PostgreSQL (a modelagem inicial está em `text/mysql.txt`).
- **Localização** — configurar `LANGUAGE_CODE = 'pt-br'` e `TIME_ZONE = 'America/Sao_Paulo'`.
- **Validações** — impedir cadastro de EPI vencido e alertar sobre EPIs próximos do vencimento.
- **Testes** — ampliar a cobertura para `editar_status`, `avisos` e autenticação.
