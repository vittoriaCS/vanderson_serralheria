from django import forms
from .models import Colaborador
from .models import EPI
from .models import Registrar
from datetime import date, datetime
from .models import Aviso
from django.core.exceptions import ValidationError

class ColaboradorForm(forms.ModelForm):
    class Meta: 
        model = Colaborador
        fields = ['nome', 'email', 'cargo', 'telefone']

class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = ['nomeEPI', 'descricao', 'validade', 'quantidade_disponivel', 'codigo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['validade'].widget.attrs.update({'placeholder': 'AAAA-MM-DD'})
 
class RegistrarForm(forms.ModelForm):
    class Meta:
        model = Registrar
        fields = ['equipamento', 'colaborador', 'status', 'condicao_equipamento', 'observacao', 'data_devolucao', 'data_emprestimo', 'data_prevista_da_devolucao']

    equipamento = forms.ModelChoiceField(queryset=EPI.objects.all(), empty_label="Selecione o EPI")
    colaborador = forms.ModelChoiceField(queryset=Colaborador.objects.all(), empty_label="Selecione o Colaborador")

    data_emprestimo = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': 'aaaa-mm-dd'})
    )
    data_devolucao = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'aaaa-mm-dd'})
    )
    data_prevista_da_devolucao = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': 'aaaa-mm-dd'})
    )

    condicao_equipamento = forms.ChoiceField(
        choices=[('', 'Selecionar condição')] + Registrar.CONDICOES_CHOICES,
        widget=forms.Select,
        label="Condição do Equipamento"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [('', 'Selecionar status')] + list(Registrar.STATUS_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        observacao = cleaned_data.get('observacao')
        datadevolucao = cleaned_data.get('data_devolucao')

        if status in ['devolvido', 'danificado', 'perdido']:
            if not observacao:
                self.add_error('observacao', 'Item não foi cadastrado: preencher campo observação.')
            if not datadevolucao:
                self.add_error('data_devolucao', 'Item não foi cadastrado: preencher campo data de devolução.')

        data_prevista = cleaned_data.get('data_prevista_da_devolucao')
        if data_prevista and data_prevista <= date.today():
            raise ValidationError("A data prevista para devolução deve ser posterior à data atual.")

        return cleaned_data
