.PHONY: help dev up down build migrate migrate-create backtest paper live test lint format clean logs shell-backend shell-db seed

# Variables
DOCKER_COMPOSE = docker-compose
BACKEND_CONTAINER = nexitrade_backend
POSTGRES_CONTAINER = nexitrade_postgres

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Levantar todo el sistema en modo desarrollo
	@echo "🚀 Iniciando NexiTrade en modo desarrollo..."
	@if [ ! -f .env ]; then echo "⚠️  No existe .env, copiando desde .env.example..."; cp .env.example .env; fi
	$(DOCKER_COMPOSE) up --build

up: ## Levantar servicios (sin rebuild)
	$(DOCKER_COMPOSE) up -d

down: ## Detener todos los servicios
	$(DOCKER_COMPOSE) down

build: ## Construir imágenes Docker
	$(DOCKER_COMPOSE) build

migrate: ## Aplicar migraciones de base de datos
	@echo "📊 Aplicando migraciones..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) alembic upgrade head

migrate-create: ## Crear nueva migración (uso: make migrate-create MSG="descripcion")
	@if [ -z "$(MSG)" ]; then echo "❌ Debes especificar MSG. Ejemplo: make migrate-create MSG='add_users_table'"; exit 1; fi
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) alembic revision --autogenerate -m "$(MSG)"

backtest: ## Ejecutar backtests y walk-forward
	@echo "📈 Ejecutando backtests..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python -m scripts.run_backtest

paper: ## Iniciar paper trading
	@echo "📄 Iniciando paper trading..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python -m scripts.run_paper

live: ## Iniciar live trading (REQUIERE CONFIRMACIÓN)
	@echo "⚠️  ¡ATENCIÓN! Vas a iniciar LIVE TRADING con dinero real."
	@echo "¿Estás seguro? Escribe 'i-know-what-im-doing' para continuar:"
	@read confirmation; \
	if [ "$$confirmation" = "i-know-what-im-doing" ]; then \
		echo "🔴 Iniciando LIVE trading..."; \
		$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python -m scripts.run_live; \
	else \
		echo "❌ Cancelado."; \
		exit 1; \
	fi

test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) pytest tests/ -v --cov=./ --cov-report=html

lint: ## Ejecutar linter
	@echo "🔍 Ejecutando linter..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) ruff check .
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) mypy . --ignore-missing-imports

format: ## Formatear código
	@echo "✨ Formateando código..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) black .
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) ruff check --fix .

clean: ## Limpiar archivos temporales y caches
	@echo "🧹 Limpiando..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf logs/*.log

logs: ## Ver logs de todos los servicios
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## Ver logs del backend
	$(DOCKER_COMPOSE) logs -f $(BACKEND_CONTAINER)

shell-backend: ## Abrir shell en el contenedor backend
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) /bin/bash

shell-db: ## Abrir psql en la base de datos
	$(DOCKER_COMPOSE) exec $(POSTGRES_CONTAINER) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

seed: ## Descargar datos históricos y entrenar modelos iniciales
	@echo "🌱 Descargando datos históricos..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python -m scripts.seed_data
	@echo "🤖 Entrenando modelos ML/RL iniciales..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python -m scripts.train_models

stop-trading: ## Detener trading (kill-switch)
	@echo "🛑 Activando kill-switch..."
	curl -X POST http://localhost:8080/api/kill \
		-H "Authorization: Bearer $(shell grep ADMIN_TOKEN .env | cut -d '=' -f2)"

status: ## Ver estado del sistema
	@echo "📊 Estado de NexiTrade:"
	@$(DOCKER_COMPOSE) ps
	@echo "\n📈 Estado de trading:"
	@curl -s http://localhost:8080/api/status | python -m json.tool || echo "Backend no disponible"

restart: down up ## Reiniciar todos los servicios

reset-db: ## ⚠️  RESETEAR base de datos (BORRA TODO)
	@echo "⚠️  ¡ATENCIÓN! Vas a BORRAR TODA LA BASE DE DATOS."
	@echo "¿Estás seguro? Escribe 'yes' para continuar:"
	@read confirmation; \
	if [ "$$confirmation" = "yes" ]; then \
		echo "🗑️  Eliminando base de datos..."; \
		$(DOCKER_COMPOSE) down -v; \
		$(DOCKER_COMPOSE) up -d postgres; \
		sleep 5; \
		$(DOCKER_COMPOSE) up -d backend; \
		sleep 5; \
		$(MAKE) migrate; \
		echo "✅ Base de datos reseteada."; \
	else \
		echo "❌ Cancelado."; \
	fi

