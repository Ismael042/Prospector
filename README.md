# Prospector

Automação de prospecção de leads: busca negócios locais (EUA/Canadá) via **Google
Places API**, identifica quem não tem site próprio e organiza os dados pra virar
oportunidade de venda de serviços de desenvolvimento web.

Projeto em desenvolvimento por fases — este repositório acompanha o roadmap público
de construção de um produto real, do zero.

## Roadmap

- [x] **Fase 0 — Setup**: repositório, credenciais, estrutura do projeto
- [x] **Fase 1 — Descoberta & Filtro**: buscar negócios por categoria/região e
      identificar quem não tem site real
- [x] **Fase 2 — Geração de Isca (IA)**: copy personalizada + mockup de landing page
      gerados por LLM para cada lead
- [x] **Fase 3 — Outreach**: roteiro de ligação personalizado por lead (a Places
      API não retorna e-mail do negócio, então o canal virou telefone)
- [x] **Fase 4 — CRM / Dashboard**: funil de vendas em Next.js + Supabase, com
      autenticação e métricas de conversão
- [ ] **Fase 5 — Deploy & Operação**: agendamento, hospedagem e monitoramento

## Módulo 1 — Descoberta & Filtro

Busca negócios por categoria + região usando a **Places API (New)** do Google e
filtra quem não tem um site próprio (campo `websiteUri` ausente, ou apenas um link
de rede social como "site").

### Setup

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Ative a **Places API (New)**
3. Crie uma credencial de API key e restrinja-a à Places API (New)
   — billing precisa estar habilitado na conta, mas há cota gratuita mensal
4. Copie `.env.example` para `.env` e cole sua chave:
   ```
   GOOGLE_PLACES_API_KEY=sua_chave_aqui
   ```
5. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Uso

```bash
python -m prospector.search --category "plumber" --location "Austin, TX" --max-results 60
```

Gera um CSV em `data/` com os negócios encontrados e a coluna `has_real_site`
indicando quem é um lead qualificado (sem site próprio).

## Fase 2 — Geração de Isca (IA)

Para cada lead sem site de um CSV do Módulo 1, gera com a **Claude API**
(`claude-opus-5`) uma copy de e-mail personalizada e um mockup completo de landing
page em HTML — auto-contido, sem dependências externas.

### Setup adicional

1. Crie uma API key em [console.anthropic.com](https://console.anthropic.com/)
2. Adicione em `.env`:
   ```
   ANTHROPIC_API_KEY=sua_chave_aqui
   ```

### Uso

```bash
python -m prospector.generate --input data/results_bakery_halifax-ns_...csv --category "bakery" --limit 5
```

Salva `email.txt`, `landing.html` e `call_script.txt` em
`data/leads/<nome-do-negocio>/`, e imprime o custo aproximado da chamada à API no
final. Custo real medido: ~$0.02-0.05 por lead com `claude-opus-5`.

## Fase 3 — Outreach

A Google Places API não expõe e-mail do negócio — só telefone, endereço e site.
Em vez de e-mail em massa (que também traria risco de compliance real, CAN-SPAM
nos EUA e CASL no Canadá), o canal de contato é telefone: `call_script.txt` traz
abertura, pontos-chave e fechamento personalizados pra uma ligação de verdade,
feita por uma pessoa — não há envio automatizado nesta fase. O `email.txt` da
Fase 2 continua sendo gerado como rascunho opcional (com rodapé de compliance:
razão social, CNPJ e endereço do MEI), caso o lead prefira e-mail depois do
primeiro contato.

## Fase 4 — CRM / Dashboard

Funil de vendas (encontrado → contatado → respondeu → reunião → fechado/perdido)
persistido em **Supabase local** (via Docker, `supabase start`) e visualizado num
dashboard **Next.js + Tailwind** em `dashboard/`, protegido por login
(Supabase Auth) e com uma tela de métricas de conversão por categoria/região.

### Setup adicional

1. Instale o [Supabase CLI](https://supabase.com/docs/guides/cli) e o Docker Desktop
2. Na raiz do repo: `supabase start` (sobe o stack local; a primeira vez baixa as
   imagens Docker)
3. Copie a `secret key` impressa pelo comando pro `.env`:
   ```
   SUPABASE_URL=http://127.0.0.1:55321
   SUPABASE_SECRET_KEY=sua_chave_aqui
   ```
4. Sincronize os leads sem site de um CSV do Módulo 1:
   ```bash
   python -m prospector.sync_supabase --input data/results_bakery_halifax-ns_...csv --category "bakery" --location "Halifax, NS"
   ```
5. Rode o dashboard:
   ```bash
   cd dashboard
   cp .env.local.example .env.local  # preencha com a URL e a chave publishable do Supabase
   npm install
   npm run dev
   ```
6. Acesse `http://localhost:3000` — primeira vez, clique em "Primeira vez? Criar
   conta" pra criar seu login (Supabase Auth local, sem confirmação de e-mail
   necessária se `enable_confirmations` estiver desligado, senão confira o
   Mailpit em `http://127.0.0.1:55324`)

A tabela `leads` tem RLS habilitado — só usuários autenticados leem/atualizam
pelo dashboard; o `sync_supabase.py` insere via `service_role`, que ignora RLS.

> Nota: o Supabase Studio local (`http://127.0.0.1:55323`) está desabilitado
> nesta máquina por um bug de mount do Docker Desktop no Windows — ver item no
> Backlog do Trello. Os dados são inspecionáveis via REST API ou psql direto.

## Stack

Python · Google Places API · Claude API (Anthropic) · Next.js · Tailwind CSS ·
Supabase (Postgres, self-hosted via Docker)

## Licença

MIT — ver [LICENSE](LICENSE).
