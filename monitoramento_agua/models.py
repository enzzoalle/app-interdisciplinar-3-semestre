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
