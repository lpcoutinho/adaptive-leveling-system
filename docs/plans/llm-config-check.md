# Plano: Verificação de Configuração de LLM

## Objetivo

Implementar uma validação no backend para verificar se o provedor de LLM selecionado (ex: Groq) possui as credenciais necessárias configuradas e refletir esse status no frontend. Isso evita erros genéricos (500) e melhora a experiência do usuário (UX).

## Passos de Implementação

### 1. Backend: Factory de LLM

- Adicionar o método estático `is_configured()` na classe `LLMFactory` em `backend/llm/factory.py`.
- Lógica:
  - Se `mock`: retorna `True`.
  - Se `groq`: verifica se `GROQ_API_KEY` existe e tem tamanho mínimo.
  - Outros provedores: lógica similar.

### 2. Backend: Endpoint de Health Check

- Atualizar a rota `/detailed` em `backend/api/routes/health.py`.
- Incluir o campo `"llm_configured": bool` chamando o método da Factory.

### 3. Frontend: Feedback ao Usuário

- Modificar `frontend/app/pages/prerequisites.py`.
- Ao carregar a página, verificar o status de configuração.
- Se o LLM não estiver pronto:
  - Ocultar o botão de análise.
  - Exibir um alerta informando que as chaves de API estão ausentes no arquivo `.env`.

## Verificação

- Rodar o backend com `LLM_PROVIDER=groq` e sem chave -> O frontend deve exibir o alerta.
- Rodar com `LLM_PROVIDER=mock` -> O frontend deve permitir a análise.
