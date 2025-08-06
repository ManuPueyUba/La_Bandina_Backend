# La Bandina Backend - Docker Commands

.PHONY: help build up down logs clean restart shell

help: ## Show this help message
	@echo "La Bandina Backend - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

logs-api: ## Show logs from API service only
	docker-compose logs -f api

logs-db: ## Show logs from database service only
	docker-compose logs -f db

restart: ## Restart all services
	docker-compose restart

clean: ## Remove all containers, images and volumes
	docker-compose down -v
	docker-compose rm -f
	docker system prune -f

shell: ## Access shell in the API container
	docker-compose exec api bash

dev: ## Start in development mode with live reload
	docker-compose up

ps: ## Show running containers
	docker-compose ps

migrate: ## Run database migrations
	docker-compose exec api python create_db.py
