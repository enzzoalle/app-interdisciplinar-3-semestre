from django import forms
from .models import ConfiguracaoSistema

class ConfiguracaoSistemaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = ['preco_metro_cubico', 'vazao_media_hora']
        widgets = {
            'preco_metro_cubico': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vazao_media_hora': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
        }