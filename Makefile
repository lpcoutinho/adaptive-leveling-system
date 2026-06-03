# Adaptive Leveling System - Makefile
# Facilita comandos comuns de desenvolvimento

.PHONY: help install update lint format type-check test test-cov clean up down logs migrate

# Variáveis
POETRY := poetry
DOCKER_COMPOSE := docker compose

help: ## Mostra este help
	@echo "Adaptive Leveling System - Comandos Disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Instalação e Configuração
install: ## Instala dependências com Poetry
	$(POETRY) install
	@echo "✅ Dependências instaladas"
	@pre-commit install || echo "⚠️  Instale pre-commit: pip install pre-commit"

update: ## Atualiza dependências
	$(POETRY) update
	@echo "✅ Dependências atualizadas"

# Qualidade de Código
lint: ## Executa Ruff linting
	$(POETRY) run ruff check .

format: ## Formata código com Ruff
	$(POETRY) run ruff format .

type-check: ## Executa MyPy type checking
	$(POETRY) run mypy .

check: lint type-check ## Executa todas as verificações (lint + type-check)

security: ## Executa Bandit security scan
	$(POETRY) run bandit -c pyproject.toml -r backend/

# Pre-commit
pre-commit: ## Executa pre-commit em todos os arquivos
	pre-commit run --all-files

pre-commit-files: ## Executa pre-commit apenas nos arquivos estagiados (git add)
	@STAGED_FILES=$$(git diff --name-only --cached); \
	if [ -n "$$STAGED_FILES" ]; then \
		pre-commit run --files $$STAGED_FILES; \
	else \
		echo "⚠️  Nenhum arquivo no staging. Use 'git add' primeiro."; \
	fi

pre-commit-update: ## Atualiza hooks pre-commit
	pre-commit autoupdate

# Testes
test: ## Executa testes
	$(POETRY) run pytest -v

test-cov: ## Executa testes com cobertura
	$(POETRY) run pytest --cov=backend --cov-report=term-missing --cov-report=html
	@echo "📊 Relatório HTML: htmlcov/index.html"

# Infraestrutura
up: ## Sobe containers Docker
	$(DOCKER_COMPOSE) up -d
	@echo "⏳ Aguardando serviços..."
	@timeout 60s bash -c "until docker inspect --format='{{.State.Health.Status}}' als-db | grep -q healthy; do sleep 2; done"
	@timeout 60s bash -c "until docker inspect --format='{{.State.Health.Status}}' als-s3 | grep -q healthy; do sleep 2; done"
	@timeout 60s bash -c "until docker inspect --format='{{.State.Health.Status}}' als-cache | grep -q healthy; do sleep 2; done"
	@echo "✅ Serviços prontos!"

down: ## Para containers Docker
	$(DOCKER_COMPOSE) down

restart: down up ## Reinicia containers

logs: ## Mostra logs dos containers
	$(DOCKER_COMPOSE) logs -f

ps: ## Lista containers em execução
	$(DOCKER_COMPOSE) ps

# Banco de Dados
migrate: ## Executa migrations no PostgreSQL
	docker exec -i als-db psql -U postgres -d postgres < migrations/001_initial_schema.sql
	@echo "✅ Schema criado"

db-shell: ## Abre shell do PostgreSQL
	docker exec -it als-db psql -U postgres -d postgres

cache-shell: ## Abre shell do Valkey
	docker exec -it als-cache valkey-cli

# S3/Minio
s3-shell: ## Abre shell do Minio
	docker exec -it als-s3 /bin/sh

# Aplicações
backend: ## Inicia backend FastAPI
	$(POETRY) run uvicorn backend.main:app --reload --port 8000

frontend: ## Inicia frontend Streamlit
	$(POETRY) run streamlit run frontend/app/app.py

# Limpeza
clean: ## Limpa arquivos de cache e temporários (Python, Pytest, MyPy, Ruff)
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov .pre-commit-cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage.*" -delete
	@echo "🧹 Limpeza de arquivos temporários concluída"

clean-poetry: ## Limpa o ambiente virtual (Virtualenv) do Poetry
	$(POETRY) env remove --all 2>/dev/null || true
	@echo "🧹 Ambiente Virtual removido"

clean-all: clean clean-poetry down ## Limpeza completa (arquivos + virtualenv + containers)
	docker system prune -f --volumes
	@echo "🧹 Todo o sistema foi limpo (incluindo volumes docker)"

# Diagnóstico
health: ## Verifica saúde dos serviços
	@echo "🏥 Health Check:"
	@echo -n "PostgreSQL: "
	@docker exec als-db pg_isready -U postgres 2>/dev/null && echo "✅ Saudável" || echo "❌ Não saudável"
	@echo -n "Valkey: "
	@docker exec als-cache valkey-cli ping 2>/dev/null | grep -q PONG && echo "✅ Saudável" || echo "❌ Não saudável"
	@echo -n "Minio: "
	@curl -s http://localhost:9005/minio/health/live > /dev/null && echo "✅ Saudável" || echo "❌ Não saudável"
	@echo -n "Jaeger: "
	@curl -s http://localhost:16686 > /dev/null && echo "✅ Saudável" || echo "❌ Não saudável"

# CI/CD (local)
ci: up migrate check test ## Simula pipeline CI completo

# Setup inicial
setup: install up migrate ## Setup completo do projeto
	@echo "🚀 Projeto configurado!"
	@echo "💡 Execute 'make help' para ver todos os comandos"
