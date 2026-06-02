import json
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import RegistroFaltaDeAgua, ConfiguracaoSistema
from .forms import ConfiguracaoSistemaForm


def _validar_api_key(request: HttpRequest) -> bool:
    api_key = getattr(settings, 'ESP32_API_KEY', '')
    if not api_key:
        return True

    header_key = request.headers.get('X-API-KEY')
    query_key = request.GET.get('api_key')
    return (header_key == api_key) or (query_key == api_key)


def _montar_intervalos_sem_agua(registros: QuerySet[RegistroFaltaDeAgua], config: ConfiguracaoSistema):
    # Comprime entradas duplicadas consecutivas e gera intervalos (0 -> 1)
    eventos = []
    ultimo_estado = None
    for r in registros.order_by('dataEHoraDoRegistro', 'id'):
        if ultimo_estado is None or r.estadoDoFluxo != ultimo_estado:
            eventos.append(r)
            ultimo_estado = r.estadoDoFluxo

    if config.preco_metro_cubico and config.vazao_media_hora:
        custo_por_segundo = (config.vazao_media_hora * config.preco_metro_cubico) / Decimal('3600')
    else:
        custo_por_segundo = Decimal('0')

    intervalos = []
    inicio = None
    for ev in eventos:
        if ev.estadoDoFluxo == 0 and inicio is None:
            inicio = ev.dataEHoraDoRegistro
        elif ev.estadoDoFluxo == 1 and inicio is not None:
            fim = ev.dataEHoraDoRegistro
            duracao = fim - inicio
            
            segundos = Decimal(duracao.total_seconds())
            economia = segundos * custo_por_segundo

            intervalos.append(
                {
                    'inicio': inicio,
                    'fim': fim,
                    'duracao': str(duracao).split('.')[0],
                    'economia': round(economia, 2),
                }
            )
            inicio = None

    if inicio is not None:
        duracaoAberta = timezone.now() - inicio
        
        segundos = Decimal(duracaoAberta.total_seconds())
        economiaAberta = segundos * custo_por_segundo

        intervalos.append(
            {
                'inicio': inicio,
                'fim': None,
                'duracao': str(duracaoAberta).split('.')[0],
                'economia': round(economiaAberta, 2),
                'custo_por_segundo': float(custo_por_segundo),
            }
        )

    return list(reversed(intervalos))


@require_GET
def index(request: HttpRequest) -> HttpResponse:
    config = ConfiguracaoSistema.load()
    registros = RegistroFaltaDeAgua.objects.all().order_by('-dataEHoraDoRegistro', '-id')[:50]
    intervalos = _montar_intervalos_sem_agua(RegistroFaltaDeAgua.objects.all(), config)

    context = {
        'registros': registros,
        'intervalos_sem_agua': intervalos,
        'config': config,
        'api_key': getattr(settings, 'ESP32_API_KEY', ''), 
    }
    return render(request, 'monitoramento_agua/index.html', context)


def configuracoes(request: HttpRequest) -> HttpResponse:
    config = ConfiguracaoSistema.load()
    if request.method == 'POST':
        form = ConfiguracaoSistemaForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações atualizadas com sucesso!')
            return redirect('monitoramento_agua:index')
    else:
        form = ConfiguracaoSistemaForm(instance=config)
    
    return render(request, 'monitoramento_agua/configuracoes.html', {'form': form})


@require_GET
def api_registros(request: HttpRequest) -> JsonResponse:
    if not _validar_api_key(request):
        return JsonResponse({'detail': 'API key inválida.'}, status=401)

    try:
        limit = int(request.GET.get('limit', '100'))
    except ValueError:
        limit = 100

    limit = max(1, min(limit, 1000))

    registros = (RegistroFaltaDeAgua.objects.all().order_by('-dataEHoraDoRegistro', '-id')[:limit])

    data = [
        {
            'id': r.id,
            'estadoDoFluxo': r.estadoDoFluxo,
            'estadoDoFluxoLabel': r.get_estadoDoFluxo_display(),
            'dataEHoraDoRegistro': r.dataEHoraDoRegistro.isoformat(),
        }
        for r in registros
    ]

    return JsonResponse({'count': len(data), 'results': data})


@csrf_exempt
@require_http_methods(['POST'])
def api_criar_registro(request: HttpRequest) -> JsonResponse:
    if not _validar_api_key(request):
        return JsonResponse({'detail': 'API key inválida.'}, status=401)

    content_type = request.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
            estado = payload.get('estadoDoFluxo')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON inválido.'}, status=400)
    else:
        estado = request.POST.get('estadoDoFluxo')

    try:
        estado = int(estado)
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'Campo estadoDoFluxo é obrigatório (0 ou 1).'}, status=400)

    if estado not in (0, 1):
        return JsonResponse({'detail': 'estadoDoFluxo deve ser 0 ou 1.'}, status=400)

    registro = RegistroFaltaDeAgua.objects.create(estadoDoFluxo=estado)

    return JsonResponse(
        {
            'id': registro.id,
            'estadoDoFluxo': registro.estadoDoFluxo,
            'dataEHoraDoRegistro': registro.dataEHoraDoRegistro.isoformat(),
            'mensagem': 'Registro criado com sucesso!'
        },
        status=201,
    )