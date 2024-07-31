# Makefile for PDM Python project

# Default target
.DEFAULT_GOAL := help

# Define variables
PYTHON := python3
PDM := pdm
TEST_DIR := tests
SRC_DIR := src
LINT_DIRS := $(SRC_DIR) $(TEST_DIR)
PROJ_NAME := money_movement
PROJECT_ROOT := $(shell pwd)
PYTHONPATH := $(shell pwd)/$(SRC_DIR)

# Targets
.PHONY: help install test lint clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'


setup: ## Setup project dependencies using PDM
	$(PDM) init
	$(PDM) install	

install: ## Install project dependencies using PDM
	$(PDM) install

test: ## Run tests using pytest
	@echo "Running tests with PYTHONPATH=$(PYTHONPATH)"
	PYTHONPATH=$(PYTHONPATH) $(PDM) run pytest $(TEST_DIR)

lint: ## Lint code using ruff
	PYTHONPATH=$(PYTHONPATH) $(PDM) run ruff check $(LINT_DIRS)

format: ## Format code using black-formatting from ruff.
	PYTHONPATH=$(PYTHONPATH) $(PDM) run ruff format $(LINT_DIRS)

run: ## Target to run the FastAPI application
	@echo "Running FastAPI application"
	PYTHONPATH=$(PYTHONPATH) $(PDM) run celery -A bridge_money_movement.tasks worker --loglevel=info & \
	PYTHONPATH=$(PYTHONPATH) $(PDM) run uvicorn money_movement.main:app --reload --host 0.0.0.0 --port 8000 & \
	wait

clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf $(TEST_DIR)/__pycache__
	rm -rf $(SRC_DIR)/__pycache__


# Docker targets
docker-test:
	docker-compose run --rm web pdm run pytest tests/

docker-run:
	docker-compose up

docker-build:
	docker-compose build

docker-lint:
	docker-compose run web pdm run ruff check $(LINT_DIRS)

docker-format:
	docker-compose run web pdm run ruff format $(LINT_DIRS)

clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf $(TEST_DIR)/__pycache__
	rm -rf $(SRC_DIR)/__pycache__


