from django.db import models
from django.utils import timezone


class RegistroFaltaDeAgua(models.Model):
	ESTADOS_POSSIVEIS_DO_FLUXO = [
		(0, 'Sem fluxo de água'),
		(1, 'Com fluxo de água'),
	]

	estadoDoFluxo = models.IntegerField(
		choices=ESTADOS_POSSIVEIS_DO_FLUXO,
		verbose_name='Estado do Fluxo de Água',
	)

	dataEHoraDoRegistro = models.DateTimeField(
		default=timezone.now,
		verbose_name='Data e Hora do Registro',
	)

	class Meta:
		verbose_name = 'Registro de Falta de Água'
		verbose_name_plural = 'Registros de Falta de Água'
		ordering = ['dataEHoraDoRegistro', 'id']

	def __str__(self):
		return (
			f"Estado: {self.get_estadoDoFluxo_display()} "
			f"no horário {self.dataEHoraDoRegistro}"
		)

class ConfiguracaoSistema(models.Model):
    preco_metro_cubico = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, 
        verbose_name="Preço por m³ (R$)"
    )
    vazao_media_hora = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000, 
        verbose_name="Vazão Média por Hora (m³)",
        help_text="Estimativa de quantos metros cúbicos seriam consumidos por hora."
    )

    def save(self, *args, **kwargs):
        # Garante que sempre teremos apenas um registro (Singleton) com ID = 1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Método auxiliar para carregar a configuração facilmente
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"