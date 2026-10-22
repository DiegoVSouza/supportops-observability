# Observabilidade de agentes — conhecimento

## Traces, métricas e logs

Traces mostram a árvore causal de uma execução e ajudam a localizar a chamada lenta ou com erro. Métricas agregam séries temporais de baixo custo operacional e alimentam SLOs e alertas. Logs registram eventos detalhados; trace ID e span ID correlacionam cada evento à execução. Não use logs como substitutos para métricas agregadas.

## Convenções GenAI e cardinalidade

As convenções semânticas GenAI do OpenTelemetry permanecem experimentais; confira a versão antes de depender de atributos. Aqui, APIs estáveis de traces são combinadas com atributos `supportops.*`. Custo e latência do LLM são valores fornecidos pelo chamador. IDs de usuário, ticket, prompt e argumentos não são labels de métricas. Modelo e provedor são span attributes, pois labels de alta cardinalidade podem elevar consumo e custo.

## SLI, SLO e custo como métrica

SLIs possíveis incluem sucesso por tarefa, taxa de erro de tools, p95 de latência e completude de saída. Um SLO deve ter janela, população e limite acordados com o serviço; os limiares do laboratório são exemplos, não metas de produção. Custo merece série própria: relacione gasto, tokens, volume, sucesso e repetição de execução. O pacote não consulta tabela de preços e não calcula qualidade do modelo.

## Sampling e privacidade

Sampling reduz volume de traces, mas deve preservar erros e execuções raras. Planeje a taxa segundo orçamento, retenção e investigação necessária. Conteúdo de prompt e resultado pode conter dados pessoais ou segredos: permanece fora dos traces por padrão. Se uma investigação exigir conteúdo, registre a decisão, limite acesso e retenção e habilite captura de forma explícita. Trace IDs também podem se tornar dados correlacionáveis quando ligados a identidades externas.

## Respostas para entrevista

**EN — How do you debug a slow agent?** Follow the trace from the agent span into its tool, HTTP, database, and LLM children. Compare durations and error status, then corroborate with aggregate p95 and correlated logs. Avoid attributing parent latency to a child until the span tree supports it.

**PT — Como depurar um agente lento?** Siga o trace do span do agente até os filhos de tool, HTTP, banco e LLM. Compare duração e status de erro e confirme com p95 agregado e logs correlacionados. Não atribua a latência do pai a um componente sem confirmar a árvore de spans.

**EN — How do you detect agent loops safely?** Track bounded step history and normalize structured tool arguments. Detect repeated tool/action sequences, repeated state cycles, and explicit step-limit overruns. Test each signal against varied healthy traffic to control false positives; keep a reset boundary between runs.

**PT — Como detectar loops com segurança?** Mantenha histórico limitado de passos e normalize argumentos estruturados. Detecte repetição de ações/tools, ciclos de estado e ultrapassagem explícita do limite de passos. Teste os sinais com tráfego saudável variado para controlar falsos positivos e limpe o detector entre execuções.

**EN — Why avoid prompt content in telemetry?** Traces are broadly searchable and retained for operational analysis. Content may contain private data or credentials. Correlation IDs, token counts, latency, outcome, and explicit content-capture controls usually support debugging with less exposure.

**PT — Por que evitar prompts na telemetria?** Traces costumam ser pesquisáveis e retidos para análise operacional. O conteúdo pode conter dados privados ou credenciais. IDs de correlação, contagem de tokens, latência, resultado e controles explícitos de captura geralmente ajudam a depurar com menor exposição.
## Phase 009 accepted local service gates

The reproducible command is `uv run --locked python scripts/check_full.py`. It runs unit/package checks, Docker `promtool check rules` and `test rules`, then the isolated local service flow. Evidence in `artifacts/evidence/phase-009-full-gate-v013-final.txt` and `phase-009-full-gate-v013-detail-final.txt` records exit 0. The service run uses P01 0.1.1 and P04 0.1.3 wheels, LocalStack SQS, PostgreSQL, HTTP, Jaeger, Grafana, and Prometheus; it exercises three synthetic incidents and all four synthetic alerts.

Setting `P03_SKIP_SERVICES=1` intentionally omits a required gate. The full check reports INCOMPLETE and exits 2, saved in `phase-009-fail-closed.txt` and `phase-009-fail-closed-detail.txt`. Metrics and model quality from production traffic remain PENDING; the local fixtures do not support production readiness claims.
