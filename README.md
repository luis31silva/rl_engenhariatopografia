<div align="center">

<img src="docs/images/logo.png" alt="RL Engenharia & Topografia" height="120" />

# RL Eng & Top — Plataforma de Gestão

**Aplicação web full-stack que substitui a folha de Excel de um gabinete de engenharia e topografia por uma plataforma moderna de gestão de trabalhos, prazos, pagamentos e finanças.**

[Ver demo](https://rl-engenhariatopografia-1.onrender.com) · Feito com FastAPI · React · TypeScript · MySQL

</div>

---

## O problema

Um gabinete de engenharia e topografia geria todo o negócio numa única folha de Excel com macros: centenas de trabalhos, várias especialidades por trabalho, prazos, pagamentos, colaboradores externos e um relatório financeiro anual — tudo à mão, propenso a erros e difícil de consultar.

## A solução

Uma aplicação web que digitaliza esse fluxo, acessível no computador ou no telemóvel, com os dados históricos migrados da própria folha original (mais de **900 trabalhos** desde 2015).

<div align="center">
<img src="docs/images/trabalhos.png" alt="Lista de trabalhos" width="80%" />
<br/><em>Lista de trabalhos com pesquisa, filtros e estado de cada especialidade</em>
</div>

---

## O que faz

### Gestão de trabalhos
Cada trabalho pode ter **várias especialidades** (levantamento topográfico, estabilidade, arquitetura, etc.), cada uma com o seu valor, datas, colaborador externo e estado próprio. Pesquisa por cliente/referência, filtros avançados (especialidade, intermediário, externo, ano, estado, situação de pagamento), ordenação e paginação.

### Estado de desempenho automático
Cada especialidade é classificada automaticamente em **TOP / OK / MAU** consoante o tempo de entrega face aos prazos definidos — replicando (e automatizando) a lógica que existia na folha original.

### Ponto de situação de pagamento
Controlo visual do pagamento por especialidade (**Pago / Falta pagamento / Em curso**), com cores intuitivas, editável individualmente ou aplicável a todo o trabalho de uma vez.

### Alertas de prazos
Painel que destaca os trabalhos a aproximar-se do prazo ou já em atraso, para nada passar ao lado.

<div align="center">
<img src="docs/images/dashboard.png" alt="Relatório de Contas" width="80%" />
<br/><em>Relatório de Contas: evolução anual, custos, liquidez e depreciação de equipamento</em>
</div>

### Relatório financeiro
Dashboard com receitas, custos e resultados líquidos por ano, percentagem de liquidez, variação anual e **previsão de depreciação de equipamento**. Gestão de custos fixos anuais e de equipamentos diretamente na aplicação.

### Faturas e recibos em PDF
Geração de recibos em PDF a partir de qualquer trabalho, com os dados do gabinete e das especialidades.

### Análise de intermediários e externos
Estatísticas por quem angaria trabalho (nº de trabalhos, valor total, valor médio, e valores do ano corrente) e por colaborador externo (nº de trabalhos e total pago).

---

## Destaques técnicos

- **Full-stack** com separação limpa entre API (FastAPI) e SPA (React + TypeScript).
- **Modelação de domínio real**: relação trabalho → múltiplas especialidades, com refactor de esquema e migração de dados históricos reais.
- **Migração de dados a partir de Excel**, incluindo leitura de estados a partir de **cores de células** e reconciliação de referências duplicadas.
- **Autenticação JWT**, filtros/paginação server-side, agregações financeiras e geração de PDF.
- **~99 testes automatizados** (pytest) a cobrir a lógica de negócio e a API.
- **Migrações de esquema versionadas** (Alembic), compatíveis com SQLite (dev) e MySQL (produção).
- **Deploy em produção**: backend + frontend no Render, base de dados MySQL gerida no Aiven.

## Stack

| Camada | Tecnologias |
|---|---|
| **Frontend** | React, TypeScript, Vite, Mantine, React Query |
| **Backend** | Python, FastAPI, SQLAlchemy, Alembic, Pydantic |
| **Base de dados** | MySQL (produção), SQLite (dev/testes) |
| **Auth & PDF** | JWT (python-jose), WeasyPrint |
| **Infraestrutura** | Render (web + static), Aiven (MySQL), Git |

---

# Documentação técnica

## Estrutura do repositório

```
backend/      API FastAPI, modelos, migrações Alembic, testes
frontend/     SPA React + Vite + TypeScript
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
   (O Aiven exige SSL; a aplicação ativa TLS por defeito na ligação MySQL via `DB_SSL`.)

### Backend — Render (Web Service)

> **Versão do Python (importante):** o Render usa por defeito uma versão muito recente
> (atualmente 3.14) que ainda não tem *wheels* pré-compilados para o `pydantic-core`, o que
> faz o build tentar compilar Rust e **falhar** (erro "Read-only file system" / maturin).
> Para evitar, o projeto fixa **Python 3.12.3** com o ficheiro `.python-version` (presente
> em `backend/.python-version` e na raiz do repositório — o Render lê este ficheiro; o antigo
> `runtime.txt` já **não** é usado). **Reforço recomendado:** definir a variável de ambiente
> `PYTHON_VERSION=3.12.3` nas definições do serviço. Depois de alterar, fazer *Clear build
> cache & deploy* para não reaproveitar o ambiente 3.14 anterior.

> **WeasyPrint (faturas PDF)** precisa de bibliotecas de sistema (Pango, Cairo, GDK-PixBuf).
> No ambiente Python nativo do Render, adicionar um ficheiro `Aptfile` na raiz do `backend`
> com: `libpango-1.0-0`, `libpangoft2-1.0-0`, `libcairo2`, `libgdk-pixbuf-2.0-0`.
> Em alternativa, usar um deploy via Docker com essas libs instaladas. Sem elas, o endpoint
> de geração de PDF falha em runtime (o resto da aplicação funciona normalmente).

- **Root Directory:** `backend`
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  (o `app.seed` cria o utilizador inicial se ainda não existir; é idempotente.)
- **Variáveis de ambiente:** `DATABASE_URL`, `SECRET_KEY`, `INITIAL_USERNAME`, `INITIAL_PASSWORD`,
  `CORS_ORIGINS` (URL do frontend), `ENVIRONMENT=production`, `PYTHON_VERSION=3.12.3`.

### Frontend — Render (Static Site)

- **Root Directory:** `frontend`
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `dist`
- **Variáveis de ambiente:** `VITE_API_BASE_URL` (URL pública do backend).

> **SPA rewrite (importante):** sendo uma Single-Page App, aceder diretamente a uma rota
> como `/login` ou recarregar a página dá "Not Found" se o servidor não reencaminhar tudo
> para o `index.html`. O projeto inclui `frontend/public/_redirects` com a regra
> `/*  /index.html  200` (copiada para `dist/` no build). Se o Render não a aplicar
> automaticamente, adicionar no dashboard do Static Site, em **Redirects/Rewrites**:
> Source `/*`, Destination `/index.html`, Action **Rewrite**.

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

O que é importado: especialidades (com prazos TOP/OK), intermediários, externos, os
trabalhos (com as suas especialidades/itens), a situação de pagamento (lida a partir das
cores das células) e os equipamentos para depreciação (aba *Relatório Contas*). Os
**custos fixos anuais** não são importados automaticamente e podem ser geridos na aplicação
(página *Relatório de Contas*).
