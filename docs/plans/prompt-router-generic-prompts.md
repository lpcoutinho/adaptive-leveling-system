# Plano: Sistema Completo de Prompts, Telemetria e Resiliência para LLM

## Status Atual

### ✅ COMPLETO (Fases 1-6)

- Sistema de roteamento de prompts
- Prompts genéricos (disciplina-agnósticos)
- Detecção de alucinações
- Métricas OpenTelemetry
- Integração com serviços

### 🔲 PENDENTE (Fases 7-11)

- Token Optimization
- Resilience Patterns (tenacity, circuit breaker)
- Prometheus + Grafana
- LangFuse Integration
- Cost Tracker

---

## Resumo de Implementação

| Fase | Componente | Status | Arquivos |
|------|------------|--------|----------|
| 1 | Prompt Router | ✅ Completo | `prompt_router.py` |
| 2 | Prompts Genéricos | ✅ Completo | 5 prompts modificados |
| 3 | Domínio/Schemas | ✅ Completo | `leveling.py`, schemas |
| 4 | Integração Services | ✅ Completo | 3 services atualizados |
| 5 | Telemetria Base | ✅ Completo | `tracer.py` com métricas |
| 6 | Hallucination Detector | ✅ Completo | `hallucination_detector.py` |
| 7 | Token Optimization | 🔲 Pendente | `token_optimizer.py` |
| 8 | Resilience Patterns | 🔲 Pendente | `circuit_breaker.py`, `retry.py` |
| 9 | Prometheus + Grafana | 🔲 Pendente | `prometheus.py`, docker configs |
| 10 | LangFuse Integration | 🔲 Pendente | `langfuse.py` |
| 11 | Cost Tracker | 🔲 Pendente | `cost_tracker.py` |

---

## 🔲 FASE 7: Token Optimization

### 7.1 Criar `backend/llm/token_optimizer.py`

**Caminho completo:** `/home/lpcoutinho/projects/test/adaptive-leveling-system/backend/llm/token_optimizer.py`

```python
"""Otimizador de tokens para redução de custos e melhoria de performance."""

import re
from typing import Callable
import tiktoken
from functools import lru_cache
from loguru import logger


class TokenOptimizer:
    """Otimiza prompts para reduzir número de tokens sem perda de qualidade."""

    def __init__(self, encoding: str = "cl100k_base"):
        """Inicializa o otimizador.

        Args:
            encoding: Nome do encoding tiktoken (default: cl100k_base para GPT-4/Groq)
        """
        self._encoding = tiktoken.get_encoding(encoding)

    def count_tokens(self, text: str) -> int:
        """Conta tokens em um texto.

        Args:
            text: Texto para contar.

        Returns:
            Número de tokens.
        """
        return len(self._encoding.encode(text))

    def compress_prompt(self, prompt: str, target_ratio: float = 0.8) -> str:
        """Comprime prompt removendo redundâncias.

        Args:
            prompt: Prompt original.
            target_ratio: Razão de compressão alvo (0.8 = 20% de redução).

        Returns:
            Prompt comprimido.
        """
        original_tokens = self.count_tokens(prompt)
        if original_tokens < 1000:  # Não comprime prompts curtos
            return prompt

        # Remove redundâncias
        compressed = self._remove_redundancies(prompt)
        compressed = self._remove_extra_whitespace(compressed)

        compressed_tokens = self.count_tokens(compressed)
        ratio = compressed_tokens / original_tokens

        logger.debug(
            f"Compressão: {original_tokens} → {compressed_tokens} tokens ({ratio:.1%})"
        )

        return compressed

    def _remove_redundancies(self, text: str) -> str:
        """Remove redundâncias do texto."""
        lines = text.split("\n")
        seen = set()
        unique_lines = []

        for line in lines:
            line_stripped = line.strip()
            if line_stripped and line_stripped not in seen:
                seen.add(line_stripped)
                unique_lines.append(line)
            elif not line_stripped:
                unique_lines.append(line)  # Preserva linhas vazias

        return "\n".join(unique_lines)

    def _remove_extra_whitespace(self, text: str) -> str:
        """Remove espaços extras."""
        text = re.sub(r" +", " ", text)
        text = re.sub(r"\n\n\n+", "\n\n", text)
        return text.strip()

    def estimate_cost(
        self, prompt_tokens: int, completion_tokens: int, provider: str, model: str
    ) -> dict:
        """Estima custo da chamada LLM em USD.

        Args:
            prompt_tokens: Tokens de entrada.
            completion_tokens: Tokens de saída.
            provider: Provider (groq, openai, anthropic).
            model: Nome do modelo.

        Returns:
            Dict com cost breakdown.
        """
        # Pricing em USD por 1M tokens (atualizar periodicamente)
        pricing = {
            "groq": {
                "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
                "mixtral-8x7b-32768": {"input": 0.27, "output": 0.27},
                "deepseek-r1": {"input": 0.14, "output": 0.28},
            },
            "openai": {
                "gpt-4": {"input": 30.0, "output": 60.0},
                "gpt-4-turbo": {"input": 10.0, "output": 30.0},
                "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            },
            "anthropic": {
                "claude-3-opus": {"input": 15.0, "output": 75.0},
                "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            },
        }

        if provider not in pricing or model not in pricing[provider]:
            logger.warning(f"Pricing não encontrado para {provider}/{model}")
            return {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0}

        rates = pricing[provider][model]
        input_cost = (prompt_tokens / 1_000_000) * rates["input"]
        output_cost = (completion_tokens / 1_000_000) * rates["output"]

        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(input_cost + output_cost, 6),
            "currency": "USD",
        }


# Cache para prompts processados
@lru_cache(maxsize=128)
def get_cached_prompt_hash(prompt: str) -> str:
    """Retorna hash do prompt para cache."""
    import hashlib
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]


def should_cache_prompt(prompt: str, min_tokens: int = 500) -> bool:
    """Determina se prompt deve ser cacheado.

    Args:
        prompt: Prompt para avaliar.
        min_tokens: Mínimo de tokens para cache.

    Returns:
        True se deve cachear.
    """
    optimizer = TokenOptimizer()
    return optimizer.count_tokens(prompt) >= min_tokens
```

### 7.2 Instalar tiktoken

```bash
poetry add tiktoken
```

### 7.3 Adicionar caching com Valkey

**Modificar `backend/llm/prompt_router.py` - adicionar método de cache:**

```python
# Dentro da classe PromptRouter, adicionar após __init__:

def get_prompt(self, use_case: PromptUseCase, version: str = "v1") -> str:
    """Retorna o prompt solicitado com cache."""
    cache_key = f"prompt:{use_case.value}:{version}"

    # Tenta cache primeiro (se habilitado)
    if self._use_cache:
        from backend.infrastructure.cache.redis_cache import get_cache
        cache = get_cache()
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Prompt carregado do cache: {cache_key}")
            return cached

    # Carrega do arquivo (com span de telemetria)
    with self._tracer.start_as_current_span("prompt.load") as span:
        # ... código existente de carregamento ...

        # Salva no cache
        if self._use_cache:
            cache = get_cache()
            cache.set(cache_key, content, ttl=3600)  # 1 hora

        return content
```

---

## 🔲 FASE 8: Resilience Patterns

### 8.1 Instalar tenacity

```bash
poetry add tenacity
```

### 8.2 Criar `backend/infrastructure/resilience/circuit_breaker.py`

**Caminho completo:** `/home/lpcoutinho/projects/test/adaptive-leveling-system/backend/infrastructure/resilience/circuit_breaker.py`

```python
"""Circuit Breaker para proteção contra falhas em cascata."""

import time
from enum import Enum
from functools import wraps
from typing import Callable
from loguru import logger


class CircuitState(Enum):
    """Estados do circuit breaker."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit Breaker pattern para LLM calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Exception | tuple = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.next_attempt = 0

    def call(self, func: Callable) -> Callable:
        """Decorator para aplicar circuit breaker."""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if time.time() < self.next_attempt:
                    raise Exception("Circuit breaker is OPEN")
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker → HALF_OPEN")

            try:
                result = await func(*args, **kwargs)
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                return result
            except self.expected_exception as e:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    self.next_attempt = time.time() + self.recovery_timeout
                    logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")
                raise

        return wrapper
```

### 8.3 Criar `backend/infrastructure/resilience/retry.py`

```python
"""Configuração de retries com tenacity."""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)
from loguru import logger


def llm_retry(max_attempts: int = 3):
    """Decorator para retries em chamadas LLM."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1.0, max=10.0),
        before_sleep=lambda retry_state: logger.warning(
            f"Retry {retry_state.attempt_number}/{max_attempts}"
        ),
    )
```

### 8.4 Aplicar aos providers

**Criar diretório primeiro:**

```bash
mkdir -p backend/infrastructure/resilience
touch backend/infrastructure/resilience/__init__.py
```

**Modificar `backend/llm/providers/groq_provider.py`:**

```python
# Adicionar imports
from backend.infrastructure.resilience.circuit_breaker import CircuitBreaker
from backend.infrastructure.resilience.retry import llm_retry

# Instância do circuit breaker
_llm_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

# Aplicar decorators ao método generate_structured
@_llm_circuit_breaker.call
@llm_retry(max_attempts=3)
async def generate_structured(self, prompt: str, response_model: type, **kwargs):
    # ... código existente ...
```

---

## 🔲 FASE 9: Prometheus + Grafana

### 9.1 Instalar prometheus-client

```bash
poetry add prometheus-client
```

### 9.2 Criar `backend/infrastructure/telemetry/prometheus.py`

```python
"""Exportador de métricas para Prometheus."""

from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Métricas
prom_llm_latency = Histogram(
    "llm_latency_seconds",
    "Latência das chamadas LLM",
    ["use_case", "provider", "model"],
)

prom_llm_tokens = Counter(
    "llm_tokens_total",
    "Total de tokens",
    ["use_case", "provider", "token_type"],
)

prom_llm_cost = Gauge(
    "llm_cost_usd",
    "Custo em USD",
    ["use_case", "provider"],
)


def start_prometheus_server(port: int = 9090):
    """Inicia servidor Prometheus."""
    start_http_server(port)
    print(f"Prometheus server on port {port}")
```

### 9.3 Adicionar ao `docker-compose.yml`

**Adicionar no final do arquivo:**

```yaml
  prometheus:
    image: prom/prometheus:latest
    container_name: adaptive_prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    ports:
      - "9091:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - adaptive_network

  grafana:
    image: grafana/grafana:latest
    container_name: adaptive_grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./docker/grafana/provisioning:/etc/grafana/provisioning
    networks:
      - adaptive_network
```

### 9.4 Criar `docker/prometheus/prometheus.yml`

```bash
mkdir -p docker/prometheus
```

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'adaptive-backend'
    static_configs:
      - targets: ['host.docker.internal:9090']
```

---

## 🔲 FASE 10: LangFuse Integration

### 10.1 Instalar langfuse

```bash
poetry add langfuse
```

### 10.2 Criar `backend/infrastructure/telemetry/langfuse.py`

```python
"""Integração com LangFuse."""

import os
from langfuse import Langfuse
from loguru import logger


class LangFuseIntegration:
    """Gerencia integração LangFuse."""

    def __init__(self):
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self._client = None

    @property
    def client(self) -> Langfuse | None:
        if not self.public_key or not self.secret_key:
            return None
        if self._client is None:
            self._client = Langfuse(
                public_key=self.public_key,
                secret_key=self.secret_key,
            )
        return self._client

    def is_enabled(self) -> bool:
        return bool(self.public_key and self.secret_key)


_langfuse: LangFuseIntegration | None = None


def get_langfuse() -> LangFuseIntegration:
    global _langfuse
    if _langfuse is None:
        _langfuse = LangFuseIntegration()
    return _langfuse
```

---

## 🔲 FASE 11: Cost Tracker

### 11.1 Criar `backend/llm/cost_tracker.py`

```python
"""Tracking de custos de LLM."""

from enum import Enum
from pydantic import BaseModel
from typing import Dict
from datetime import datetime, date


class Provider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class CostTracker:
    """Rastreia custos de LLM."""

    PRICING = {
        Provider.GROQ: {
            "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        },
        Provider.OPENAI: {
            "gpt-4": {"input": 30.0, "output": 60.0},
        },
    }

    def __init__(self):
        self._records = []

    def calculate_cost(
        self, provider: Provider, model: str,
        prompt_tokens: int, completion_tokens: int
    ) -> dict:
        """Calcula custo da chamada."""
        if provider not in self.PRICING:
            return {"total_cost_usd": 0.0}

        rates = self.PRICING[provider].get(model, {"input": 0, "output": 0})
        input_cost = (prompt_tokens / 1_000_000) * rates["input"]
        output_cost = (completion_tokens / 1_000_000) * rates["output"]

        return {
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(input_cost + output_cost, 6),
        }

    def record(self, provider, model, use_case, prompt_tokens, completion_tokens):
        """Registra um uso."""
        costs = self.calculate_cost(provider, model, prompt_tokens, completion_tokens)
        record = {
            "date": datetime.now().date(),
            "provider": provider,
            "model": model,
            "use_case": use_case,
            "total_tokens": prompt_tokens + completion_tokens,
            **costs,
        }
        self._records.append(record)
        return record


_cost_tracker: CostTracker | None = None


def get_cost_tracker() -> CostTracker:
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker
```

---

## Dependências (pyproject.toml)

**Adicionar ao `pyproject.toml`:**

```toml
[tool.poetry.dependencies]
tenacity = "^8.2.3"
prometheus-client = "^0.19.0"
langfuse = "^2.0.0"
tiktoken = "^0.5.2"
```

**Instalar tudo:**

```bash
poetry add tenacity prometheus-client langfuse tiktoken
```

---

## Variáveis de Ambiente (.env)

**Adicionar:**

```bash
# Token Optimization
PROMPT_CACHE_ENABLED=true

# LangFuse
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_secret

# Prometheus
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Cost Tracking
COST_TRACKING_ENABLED=true
```

---

## Validação Final

### Checklist de Implementação

**Fases 1-6: ✅ COMPLETO**

- [x] Prompt Router criado
- [x] Prompts genéricos (sem "Cálculo I")
- [x] `discipline_example` renomeado
- [x] Services integrados
- [x] Telemetria configurada
- [x] Hallucination detector

**Fases 7-11: 🔲 PENDENTE**

- [ ] Fase 7: Token Optimization
- [ ] Fase 8: Resilience Patterns
- [ ] Fase 9: Prometheus + Grafana
- [ ] Fase 10: LangFuse Integration
- [ ] Fase 11: Cost Tracker

### Testes

```bash
# Verificar imports
python -c "from backend.llm.token_optimizer import TokenOptimizer"
python -c "from backend.infrastructure.resilience.circuit_breaker import CircuitBreaker"
python -c "from backend.infrastructure.telemetry.prometheus import start_prometheus_server"
python -c "from backend.infrastructure.telemetry.langfuse import get_langfuse"
python -c "from backend.llm.cost_tracker import get_cost_tracker"

# Testes completos
make test
make check

# Verificar Prometheus
curl http://localhost:9091/metrics

# Verificar Grafana
curl http://localhost:3001
```

---

## Benefícios

1. **Reutilização:** Prompts disciplina-agnósticos ✅
2. **Experimentação:** A/B testing de prompts ✅
3. **Rastreabilidade:** OpenTelemetry ✅
4. **Observabilidade:** Jaeger funcionando ✅
5. **Resiliência:** Retries + Circuit Breaker 🔲
6. **Otimização:** Token compression + caching 🔲
7. **Custo Tracking:** Visibilidade completa 🔲
8. **Harness:** LangFuse para eval 🔲
9. **Dashboards:** Prometheus + Grafana 🔲
