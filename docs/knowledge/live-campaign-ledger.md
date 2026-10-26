# Ledger operacional de campanha — P03

## Aprendizado

Campanhas devem reservar chamadas e tokens antes do envio. Se a tentativa terminou sem uso conhecido, mantenha toda a reserva: converter valores desconhecidos em zero permite que a próxima etapa ultrapasse o teto. Tentativas incertas e resultados completos permanecem imutáveis e não podem ser repetidos automaticamente.

O ledger local do P03 usa eventos append-only, reserva transacional, limites cumulativos e lease do sistema operacional. A retomada é uma inspeção somente leitura que mostra identificadores e métricas operacionais, sem spans, prompts, respostas ou argumentos.

## Limites atuais

A fase não envia chamadas ao Groq e não coleta telemetria. O lease ainda não está ligado a uma execução live aprovada; também faltam dispatcher, recuperação após falha durante despacho, limites autorizados, revisão humana e preflight do catálogo. A validação full está `INCOMPLETE` porque os validadores Docker/promtool e o gate de serviços foram deliberadamente omitidos para preservar outros stacks.

## Resposta de entrevista (PT-BR)

Implementei reserva durável e limites transacionais para campanhas de observabilidade, com uma inspeção read-only que não armazena conteúdo de spans. Um teste cobre o caso de uso desconhecido e impede subcontabilização. Não afirmo que está pronto para live: ainda faltam aprovação de quota, dispatcher, integração do lease e gates operacionais.

## Interview answer (English)

I added durable reservations and transactional campaign caps for observability evaluations, with read-only inspection that does not store span content. A regression covers unknown usage so it cannot be undercounted. This is not live-ready: quota approval, dispatch, lease integration, and operational gates remain outstanding.
