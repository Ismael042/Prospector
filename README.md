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
- [ ] **Fase 4 — CRM / Dashboard**: funil de vendas em Next.js + Supabase
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

## Stack

Python · Google Places API · Claude API (Anthropic) · (próximas fases: Next.js,
Supabase)

## Licença

MIT — ver [LICENSE](LICENSE).
