from django.contrib import admin

from .models import RegistroFaltaDeAgua


@admin.register(RegistroFaltaDeAgua)
class RegistroFaltaDeAguaAdmin(admin.ModelAdmin):
	list_display = ('id', 'estadoDoFluxo', 'dataEHoraDoRegistro')
	list_filter = ('estadoDoFluxo',)
	ordering = ('-dataEHoraDoRegistro', '-id')
