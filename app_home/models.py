from django.db import models

# Create your models here.

class Colaborador(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField()
    cargo = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome

class EPI(models.Model):
    nomeEPI = models.CharField(max_length=100)
    descricao = models.CharField(max_length=150)
    validade = models.DateField()
    quantidade_disponivel = models.IntegerField()
    codigo = models.CharField(max_length=100)

    def __str__(self):
        return self.nomeEPI
    
class Registrar(models.Model):
    STATUS_CHOICES = [
        ('emprestado', 'Emprestado'),
        ('em_uso', 'Em uso'),
        ('fornecido', 'Fornecido'),
        ('devolvido', 'Devolvido'),
        ('danificado', 'Danificado'),
        ('perdido', 'Perdido'),
    ]

    CONDICOES_CHOICES = [
        ('bom', 'Bom Estado'),
        ('usado_bom', 'Usado'),
        ('manutencao', 'Em Manutenção'),
        ('quebrado', 'Quebrado/Danificado'),
        ('indisponivel', 'Indisponível'),
        ('vencido', 'Vencido'),
        ('aguardando_substituicao', 'Aguardando Substituição'),
        ('contaminado', 'Contaminado'),
        ('descartabilidade', 'Em Descartabilidade'),
    ]

    equipamento = models.ForeignKey(EPI, on_delete=models.CASCADE, related_name='registros')
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='registros')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    condicao_equipamento = models.CharField(max_length=100, choices=CONDICOES_CHOICES)
    observacao = models.CharField(max_length=100, blank=True, null=True)
    data_devolucao = models.DateField(blank=True, null=True)
    data_emprestimo = models.DateField()
    data_prevista_da_devolucao = models.DateField()

    def __str__(self):
        return f'{self.equipamento} - {self.colaborador}'

class Aviso(models.Model):
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo