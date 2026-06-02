from django.urls import path
from . import views

app_name = 'monitoramento_agua'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/registros/', views.api_registros, name='api_registros'),
    path('api/registro/', views.api_criar_registro, name='api_criar_registro'),
    path('configuracoes/', views.configuracoes, name='configuracoes')
]