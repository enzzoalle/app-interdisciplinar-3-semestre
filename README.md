# Aplicação de Monitoramento de Água

Esta é uma aplicação desenvolvida em Django para monitorar o estado do fluxo de água, permitindo o registro de quedas e retornos no abastecimento. A aplicação possui uma interface web simples para visualizar os intervalos sem água e uma API dedicada para receber dados de dispositivos IoT (como ESP32).

## 🚀 Tecnologias Utilizadas

* **Python & Django:** Framework principal (Django 6.0.5).
* **PostgreSQL:** Banco de dados relacional configurado por padrão.
* **python-dotenv:** Para gerenciamento de variáveis de ambiente de forma segura.

## 🛠️ Configuração e Instalação

1.  **Clone o repositório e acesse a pasta do projeto:**
    ```bash
    git clone <seu-repositorio>
    cd app-interdisciplinar-3-semestre
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # ou
    .venv\Scripts\activate  # Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto (onde fica o `manage.py`) e configure as variáveis utilizadas no arquivo `settings.py`:
    ```env
    DJANGO_SECRET_KEY=sua_chave_secreta_aqui
    DJANGO_DEBUG=1
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
    
    # Configurações do Banco de Dados PostgreSQL
    POSTGRES_DB=monitoramento_agua
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_HOST=127.0.0.1
    POSTGRES_PORT=5432
    
    # Chave da API (usada pelos dispositivos para enviar dados)
    ESP32_API_KEY=minha_chave_super_secreta
    ```

5.  **Execute as migrações e inicie o servidor:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

## 📡 Tutorial da API (Como consumir os endpoints)

A aplicação fornece uma API simples para listar e criar registros de fluxo de água.

### Autenticação
Se a variável `ESP32_API_KEY` estiver configurada no seu `.env`, você deverá enviar a chave de uma destas duas formas em todas as requisições para a API:
* No header da requisição: `X-API-KEY: sua_chave_aqui`
* Na URL (Query String): `?api_key=sua_chave_aqui`

### 1. Criar um Registro (Dispositivo -> Servidor)
**Rota:** `POST /api/registro/`

Este endpoint é usado pelo microcontrolador para avisar se há ou não água no momento. O campo principal é o `estadoDoFluxo`, que aceita:
* `0`: Sem fluxo de água
* `1`: Com fluxo de água

**Exemplo usando `cURL`:**
```bash
curl -X POST [http://127.0.0.1:8000/api/registro/](http://127.0.0.1:8000/api/registro/) \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: minha_chave_super_secreta" \
     -d '{"estadoDoFluxo": 0}'

```

**Exemplo em Python (Requests):**

```python
import requests

url = "[http://127.0.0.1:8000/api/registro/](http://127.0.0.1:8000/api/registro/)"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "minha_chave_super_secreta"
}
payload = {
    "estadoDoFluxo": 1  # Informando que a água voltou
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

```

**Resposta de Sucesso (201 Created):**

```json
{
    "id": 5,
    "estadoDoFluxo": 1,
    "dataEHoraDoRegistro": "2026-05-25T14:30:00+00:00",
    "mensagem": "Registro criado com sucesso!"
}

```

### 2. Listar Registros

**Rota:** `GET /api/registros/`

Retorna os registros mais recentes salvos no banco. Você pode usar o parâmetro `?limit=N` na URL para limitar o número de resultados (o padrão é 100, e o máximo é 1000).

**Exemplo usando `cURL`:**

```bash
curl -X GET "[http://127.0.0.1:8000/api/registros/?limit=5](http://127.0.0.1:8000/api/registros/?limit=5)" \
     -H "X-API-KEY: minha_chave_super_secreta"

```

**Resposta de Sucesso (200 OK):**

```json
{
    "count": 2,
    "results": [
        {
            "id": 2,
            "estadoDoFluxo": 1,
            "estadoDoFluxoLabel": "Com fluxo de água",
            "dataEHoraDoRegistro": "2026-05-25T14:30:00+00:00"
        },
        {
            "id": 1,
            "estadoDoFluxo": 0,
            "estadoDoFluxoLabel": "Sem fluxo de água",
            "dataEHoraDoRegistro": "2026-05-25T10:00:00+00:00"
        }
    ]
}

```

## 📊 Dashboard Web

Acessando a raiz da aplicação no navegador (`http://127.0.0.1:8000/`), você tem acesso ao painel de Monitoramento de Água. Ele processa os dados automaticamente, combinando as ausências (0) e retornos (1) para calcular e exibir uma tabela de **"Intervalos sem água"** com a duração exata de cada queda e uma tabela contendo todo o histórico de logs.