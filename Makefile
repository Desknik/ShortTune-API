# ShortTune API Makefile
.PHONY: help install dev test clean docker build deploy

# Variables
PYTHON := python
PIP := pip
VENV := venv
DOCKER_IMAGE := shorttune-api
DOCKER_TAG := latest

# Default target
.DEFAULT_GOAL := help

help: ## Mostra ajuda com comandos disponíveis
	@echo "ShortTune API - Comandos Disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências
	$(PIP) install -r requirements.txt

setup: ## Executa setup completo do projeto
	chmod +x setup.sh
	./setup.sh

dev: ## Inicia servidor em modo desenvolvimento
	$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

start: ## Inicia servidor em modo produção
	$(PYTHON) -m uvicorn main:app --host 0.0.0.0 --port 8000

test: ## Executa todos os testes
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Executa testes com cobertura
	$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

lint: ## Executa linting do código
	flake8 --max-line-length=100 --exclude=venv,temp,logs .
	black --check --line-length=100 .

format: ## Formata código automaticamente
	black --line-length=100 .
	isort .

clean: ## Remove arquivos temporários
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf temp/*
	rm -rf logs/*

docker-build: ## Constrói imagem Docker
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Executa container Docker
	docker run -p 8000:8000 --env-file .env $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-compose-up: ## Inicia com docker-compose
	docker-compose up --build

docker-compose-down: ## Para docker-compose
	docker-compose down

docker-clean: ## Remove imagens Docker não utilizadas
	docker system prune -f
	docker image prune -f

requirements: ## Atualiza requirements.txt
	$(PIP) freeze > requirements.txt

health: ## Verifica saúde da API
	curl -f http://localhost:8000/health || echo "API não está respondendo"

logs: ## Mostra logs da aplicação
	tail -f logs/app.log

backup: ## Faz backup dos dados importantes
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude=venv \
		--exclude=temp \
		--exclude=logs \
		--exclude=__pycache__ \
		--exclude=.git \
		.

deploy: ## Deploy para produção (exemplo)
	@echo "Implementar script de deploy específico para seu ambiente"
	@echo "Por exemplo: rsync, scp, kubectl, etc."

monitor: ## Inicia monitoramento básico
	@echo "Monitorando API em http://localhost:8000"
	@while true; do \
		echo "$(shell date): $(shell curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"; \
		sleep 30; \
	done

# Aliases para comandos comuns
run: dev ## Alias para 'make dev'
serve: start ## Alias para 'make start'
check: test ## Alias para 'make test'
