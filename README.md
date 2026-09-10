# RL Eng & Top — Gestão do Gabinete de Topografia

Aplicação web que substitui a folha de cálculo (`CONT- RLENGTOP.xlsm`) usada para gerir
o negócio de um gabinete de engenharia e topografia: registo de trabalhos, clientes,
intermediários, especialidades, dashboard financeiro, alertas de prazos e faturas em PDF.

## Stack

- **Backend:** FastAPI + SQLAlchemy + Alembic, MySQL (driver PyMySQL), JWT.
- **Frontend:** React + Vite + TypeScript + Mantine.
- **Base de dados:** MySQL (produção via Aiven). SQLite é usado por defeito em dev/testes.
- **Deploy:** Render (backend + frontend), MySQL no Aiven — feito manualmente.

## Estrutura

```
backend/    API FastAPI, modelos, migrações Alembic, testes
frontend/   SPA React + Vite + TypeScript
extrai_xlsm/  Conteúdo extraído da planilha original (referência)
```

## Desenvolvimento local

### Backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt

# Sem DATABASE_URL usa SQLite (backend/dev.db) — não precisa de MySQL local.
uvicorn app.main:app --reload
```

- API em `http://127.0.0.1:8000`
- Documentação automática (Swagger) em `http://127.0.0.1:8000/docs`
- Saúde: `http://127.0.0.1:8000/health`

Criar o utilizador inicial (login único):

```bash
cd backend
. .venv/bin/activate
# Definir INITIAL_USERNAME / INITIAL_PASSWORD no .env (ou usar os defaults admin/admin em dev).
python -m app.seed
```

Testes:

```bash
cd backend
. .venv/bin/activate
python -m pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- App em `http://localhost:5173`
- Em dev, as chamadas a `/api` são encaminhadas para o backend em `127.0.0.1:8000`
  (ver `vite.config.ts`).

## Migrações da base de dados (Alembic)

O Alembic é a **única fonte de verdade** do schema. Não existe `schema.sql`.

```bash
cd backend
. .venv/bin/activate
export DATABASE_URL="mysql+pymysql://user:pass@host:porta/bd"   # ou SQLite em dev

alembic upgrade head              # aplicar migrações
alembic revision --autogenerate -m "descricao"   # gerar nova migração
```

## Variáveis de ambiente

### Backend (`backend/.env`, ver `.env.example`)

| Variável | Descrição | Exemplo |
|---|---|---|
| `DATABASE_URL` | Ligação à BD. Sem esta, usa SQLite. | `mysql+pymysql://user:pass@host:3306/bd` |
| `SECRET_KEY` | Chave para assinar tokens JWT (usar valor forte em produção). | `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token de acesso. | `1440` |
| `INITIAL_USERNAME` | Utilizador inicial criado pelo seed. | `admin` |
| `INITIAL_PASSWORD` | Password inicial (definir valor forte). | `(password forte)` |
| `EMPRESA_NOME` | Nome do gabinete (aparece nas faturas PDF). | `RL - Engenharia & Topografia` |
| `EMPRESA_MORADA` | Morada do gabinete (faturas PDF). | `Rua ..., Santo Tirso` |
| `EMPRESA_NIF` | NIF do gabinete (faturas PDF). | `123456789` |
| `EMPRESA_CONTACTO` | Contacto (faturas PDF). | `912345678` |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula. | `https://app.onrender.com` |
| `ENVIRONMENT` | Nome do ambiente. | `production` |

### Frontend (`frontend/.env`, ver `.env.example`)

| Variável | Descrição | Exemplo |
|---|---|---|
| `VITE_API_BASE_URL` | URL base da API. | `https://api.onrender.com` |

## Deploy (manual)

> O deploy é feito manualmente. Estas notas servem de guia.

### Base de dados — Aiven (MySQL)

1. Criar um serviço MySQL no Aiven e obter a *connection string*.
2. Compor `DATABASE_URL` no formato `mysql+pymysql://user:pass@host:porta/bd`.
   (O Aiven exige SSL; para MySQL o PyMySQL negoceia TLS automaticamente na maioria
   dos casos. Se necessário, acrescentar parâmetros de SSL à connection string.)

### Backend — Render (Web Service)

> **WeasyPrint (faturas PDF)** precisa de bibliotecas de sistema (Pango, Cairo, GDK-PixBuf).
> No ambiente Python nativo do Render, adicionar um ficheiro `Aptfile` na raiz do `backend`
> com: `libpango-1.0-0`, `libpangoft2-1.0-0`, `libcairo2`, `libgdk-pixbuf-2.0-0`.
> Em alternativa, usar um deploy via Docker com essas libs instaladas. Sem elas, o endpoint
> de geração de PDF falha em runtime (o resto da aplicação funciona normalmente).

- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  (o `app.seed` cria o utilizador inicial se ainda não existir; é idempotente.)
- **Variáveis de ambiente:** `DATABASE_URL`, `SECRET_KEY`, `INITIAL_USERNAME`, `INITIAL_PASSWORD`,
  `CORS_ORIGINS` (URL do frontend), `ENVIRONMENT=production`.

### Frontend — Render (Static Site)

- **Root Directory:** `frontend`
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `dist`
- **Variáveis de ambiente:** `VITE_API_BASE_URL` (URL pública do backend).

> **CORS:** garantir que `CORS_ORIGINS` no backend inclui o domínio público do frontend,
> caso contrário o browser bloqueia as chamadas.

## Importação do histórico (.xlsm → base de dados)

Existe um script que importa os dados da folha de cálculo original para a base de dados.
Usa os modelos SQLAlchemy, pelo que funciona tanto em **SQLite** (local) como em **MySQL**
(produção) — o destino é determinado pela `DATABASE_URL`. É idempotente (identifica
trabalhos pela referência), por isso pode ser corrido mais do que uma vez sem duplicar.

Correr **depois** de aplicar as migrações (`alembic upgrade head`):

```bash
cd backend
. .venv/bin/activate

# Local (SQLite dev.db):
python -m app.importar "../CONT- RLENGTOP.xlsm"

# Produção (MySQL Aiven):
DATABASE_URL="mysql+pymysql://user:pass@host:porta/bd" python -m app.importar "../CONT- RLENGTOP.xlsm"
```

No fim, o script imprime um relatório (especialidades, intermediários, externos e
trabalhos importados/ignorados). As linhas em branco e as referências repetidas são
ignoradas automaticamente.

O que é importado: especialidades (com prazos TOP/OK), intermediários (com valor),
externos, os trabalhos (com as suas especialidades/itens) e os equipamentos para
depreciação (aba *Relatório Contas*). Os **custos fixos anuais** não são importados
automaticamente e podem ser geridos na aplicação (página *Relatório de Contas*).
